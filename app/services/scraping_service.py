from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from app.core.logging import logger
from typing import Optional, Dict, List
import uuid
import asyncio
import re

try:
    import requests
    from bs4 import BeautifulSoup
    import aiohttp
except ImportError:
    logger.warning("Scraping dependencies not installed.")

from app.integrations.scraper_clients import ScraperClient, StealthScraper, PlaywrightScraper
from app.integrations.document_chunker import DocumentChunker

# Import Playwright for headless browsing
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Some scraping features may be limited.")


class ScrapingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.scraping_jobs_collection = db.scraping_jobs
        self.scraping_results_collection = db.scraping_results
        # Lazy-initialised on first successful scrape
        self._embedding_service = None
        self._vector_service = None
        self._chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)

    async def create_scraping_job(
        self,
        url: str,
        selectors: dict,
        user_id: str,
        job_name: str = None,
        schedule: str = None,
        target_type: str = "general"
    ) -> dict:
        """Create a new web scraping job with enhanced scheduling"""
        try:
            job_id = str(uuid.uuid4())
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URL must start with http:// or https://"
                )
            
            # Calculate next run time based on schedule
            next_run = self._calculate_next_run(schedule or "manual")
            
            job_doc = {
                "job_id": job_id,
                "url": url,
                "selectors": selectors,
                "user_id": ObjectId(user_id),
                "job_name": job_name or f"Scrape: {url}",
                "status": "pending",
                "schedule": schedule or "manual",
                "target_type": target_type,  # general, news, child_violence_indicators
                "created_at": datetime.now(timezone.utc),
                "last_run": None,
                "next_run": next_run,
                "run_count": 0,
                "success_count": 0,
                "error_count": 0,
                "last_error": None,
                "enabled": True
            }
            
            await self.scraping_jobs_collection.insert_one(job_doc)
            logger.info(f"Scraping job created: {job_id} for URL: {url}, Schedule: {schedule}")
            
            return {
                "job_id": job_id,
                "url": url,
                "job_name": job_doc["job_name"],
                "status": "pending",
                "schedule": schedule or "manual",
                "next_run": next_run,
                "created_at": job_doc["created_at"]
            }
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            raise

    async def run_scraping_job(self, job_id: str, user_id: str):
        """Execute a web scraping job"""
        try:
            job = await self.scraping_jobs_collection.find_one({
                "job_id": job_id,
                "user_id": ObjectId(user_id)
            })
            
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scraping job not found"
                )
            
            await self.scraping_jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": {"status": "running"}}
            )
            
            try:
                # Scrape the website
                scraped_data = await self._scrape_website(job["url"], job["selectors"])

                result_id = str(uuid.uuid4())

                # Vectorize and store in pgvector (non-blocking on failure)
                vector_id = await self._vectorize_scraped_data(scraped_data, job, result_id)

                result_doc = {
                    "result_id": result_id,
                    "job_id": job_id,
                    "url": job["url"],
                    "data": scraped_data,
                    "timestamp": datetime.now(timezone.utc),
                    "status": "success",
                    "item_count": len(self._flatten_data(scraped_data)),
                    "vectorized": vector_id is not None,
                    "vector_id": vector_id,
                }
            except Exception as e:
                logger.error(f"Error scraping website {job['url']}: {e}")
                result_doc = {
                    "result_id": str(uuid.uuid4()),
                    "job_id": job_id,
                    "url": job["url"],
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc),
                    "status": "failed",
                    "item_count": 0,
                    "vectorized": False,
                    "vector_id": None,
                }
            
            # Store the result
            await self.scraping_results_collection.insert_one(result_doc)
            
            # Calculate next run time
            next_run = self._calculate_next_run(job.get("schedule", "manual"))
            
            # Update job status
            update_data = {
                "$set": {
                    "status": result_doc["status"],
                    "last_run": datetime.now(timezone.utc),
                    "next_run": next_run
                },
                "$inc": {
                    "run_count": 1,
                    f"{'success_count' if result_doc['status'] == 'success' else 'error_count'}": 1
                }
            }
            
            # Store last error if failed
            if result_doc["status"] == "failed":
                update_data["$set"]["last_error"] = result_doc.get("error")
            
            await self.scraping_jobs_collection.update_one(
                {"job_id": job_id},
                update_data
            )
            
            logger.info(f"Scraping job completed: {job_id} - {result_doc['status']}")
            
            return {
                "result_id": result_doc["result_id"],
                "status": result_doc["status"],
                "item_count": result_doc["item_count"],
                "url": job["url"],
                "timestamp": result_doc["timestamp"],
                "next_run": next_run,
                "data": result_doc.get("data"),
                "error": result_doc.get("error"),
                "vectorized": result_doc.get("vectorized", False),
                "vector_id": result_doc.get("vector_id"),
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error running scraping job: {e}")
            raise

    async def list_scraping_jobs(self, user_id: str, page: int = 1, limit: int = 20):
        """List user's scraping jobs"""
        try:
            filters = {"user_id": ObjectId(user_id)}
            
            total = await self.scraping_jobs_collection.count_documents(filters)
            
            jobs = await self.scraping_jobs_collection.find(filters)\
                .skip((page - 1) * limit)\
                .limit(limit)\
                .sort("created_at", -1)\
                .to_list(limit)
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "jobs": [
                    {
                        "job_id": j["job_id"],
                        "job_name": j["job_name"],
                        "url": j["url"],
                        "status": j["status"],
                        "run_count": j["run_count"],
                        "success_count": j.get("success_count", 0),
                        "error_count": j.get("error_count", 0),
                        "last_run": j["last_run"],
                        "created_at": j["created_at"],
                        "schedule": j.get("schedule", "manual")
                    }
                    for j in jobs
                ],
                "stats": {
                    "total_runs": sum(j.get("run_count", 0) for j in jobs),
                    "total_successes": sum(j.get("success_count", 0) for j in jobs),
                    "total_errors": sum(j.get("error_count", 0) for j in jobs),
                    "active_jobs": len([j for j in jobs if j.get("enabled", True)])
                }
            }
        except Exception as e:
            logger.error(f"Error listing scraping jobs: {e}")
            raise

    async def get_scraping_results(self, job_id: str, user_id: str, limit: int = 50):
        """Get results for a scraping job"""
        try:
            job = await self.scraping_jobs_collection.find_one({
                "job_id": job_id,
                "user_id": ObjectId(user_id)
            })
            
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scraping job not found"
                )
            
            results = await self.scraping_results_collection.find(
                {"job_id": job_id}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
            
            return {
                "job_id": job_id,
                "url": job["url"],
                "job_name": job["job_name"],
                "total_results": len(results),
                "results": [
                    {
                        "result_id": r["result_id"],
                        "status": r["status"],
                        "item_count": r.get("item_count", 0),
                        "timestamp": r["timestamp"],
                        "data": r.get("data"),
                        "error": r.get("error")
                    }
                    for r in results
                ]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting scraping results: {e}")
            raise

    async def delete_scraping_job(self, job_id: str, user_id: str):
        """Delete scraping job and all its results"""
        try:
            # Delete all results for this job
            await self.scraping_results_collection.delete_many(
                {"job_id": job_id}
            )
            
            # Delete the job
            result = await self.scraping_jobs_collection.delete_one({
                "job_id": job_id,
                "user_id": ObjectId(user_id)
            })
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scraping job not found"
                )
            
            logger.info(f"Scraping job deleted: {job_id}")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting scraping job: {e}")
            raise

    def _get_vector_services(self):
        """Lazily initialise embedding + vector services (same pattern as FileService)."""
        if self._embedding_service is None:
            from app.integrations.embedding_service import EmbeddingService
            from app.integrations.postgres_vector_service import PostgresVectorService

            self._embedding_service = EmbeddingService()
            self._vector_service = PostgresVectorService(
                dimension=self._embedding_service.dimension
                if self._embedding_service.available
                else 384
            )
        return self._embedding_service, self._vector_service

    async def _vectorize_scraped_data(
        self, scraped_data: dict, job: dict, result_id: str
    ) -> Optional[str]:
        """
        Chunk, embed and store scraped text in pgvector.

        Returns the vector_id (used as file_id in the DocumentChunk table)
        on success, or None if vectorization is unavailable / fails.
        The job can still be considered successful even if vectorization fails.
        """
        try:
            embedding_service, vector_service = self._get_vector_services()
            if not embedding_service.available:
                logger.warning("No embedding provider available — skipping vectorization")
                return None

            # Ensure the pgvector table exists
            await vector_service.initialize()

            # Flatten scraped_data values into a single document string
            text_parts = []
            for field, value in scraped_data.items():
                if isinstance(value, list):
                    joined = " | ".join(str(v) for v in value if v)
                    if joined:
                        text_parts.append(f"{field}: {joined}")
                elif value:
                    text_parts.append(f"{field}: {value}")

            full_text = "\n".join(text_parts).strip()
            if not full_text:
                logger.info(f"No text to vectorize for result {result_id}")
                return None

            chunks = self._chunker.chunk_text(full_text)
            chunk_texts = [c["text"] for c in chunks]
            embeddings = await embedding_service.embed_texts(chunk_texts)

            vector_id = f"scrape_{result_id}"
            metadata = {
                "source_type": "web_scrape",
                "url": job["url"],
                "job_id": job["job_id"],
                "job_name": job.get("job_name", ""),
                "result_id": result_id,
                "target_type": job.get("target_type", "general"),
            }

            await vector_service.upsert_document_chunks(
                vector_id, chunks, embeddings, metadata
            )

            logger.info(
                f"Vectorized scraping result {result_id}: "
                f"{len(chunks)} chunk(s) stored in pgvector (id={vector_id})"
            )
            return vector_id

        except Exception as exc:
            logger.warning(f"Vectorization failed for result {result_id}: {exc}")
            return None

    async def _scrape_website(self, url: str, selectors: dict) -> dict:
        """
        Scrape website using Scrapy + Playwright (primary) with a direct Playwright fallback.
        Scrapy provides middleware support (UA rotation, retry logic) on top of Playwright.
        """
        # --- Primary: Scrapy + Playwright ---
        try:
            from app.services.scrapy_runner import ScrapyRunner

            logger.info(f"Scraping {url} via Scrapy+Playwright")
            result = await ScrapyRunner.run_generic_spider(url, selectors)
            if result and result.get("scraped_data") is not None:
                logger.info(f"Scrapy+Playwright succeeded for {url}")
                return result.get("scraped_data", {})
        except Exception as exc:
            logger.warning(f"Scrapy+Playwright failed for {url}: {exc} — falling back to direct Playwright")

        # --- Fallback: direct Playwright ---
        logger.info(f"Scraping {url} via direct Playwright (fallback)")
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                # Launch browser with stealth options
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu',
                        '--hide-scrollbars',
                        '--mute-audio',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--disable-extensions',
                        '--disable-component-extensions-with-background-pages',
                    ]
                )
                
                # Create context with realistic browser fingerprint
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    device_scale_factor=1,
                    is_mobile=False,
                    has_touch=False,
                    locale='en-US',
                    timezone_id='America/New_York',
                )
                
                page = await context.new_page()
                
                # Navigate with wait
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=30000
                )
                
                if response.status == 403:
                    await browser.close()
                    raise Exception("403 Forbidden - Site is blocking scrapers even with Playwright")
                
                # Wait for network to be idle
                await page.wait_for_load_state('networkidle')
                
                # Scroll to trigger lazy loading
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                
                # Get page content
                html = await page.content()
                
                await browser.close()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                scraped_data = {}
                for field_name, css_selector in selectors.items():
                    try:
                        elements = soup.select(css_selector)
                        
                        if len(elements) == 1:
                            scraped_data[field_name] = elements[0].get_text(strip=True)
                        else:
                            scraped_data[field_name] = [
                                elem.get_text(strip=True) for elem in elements
                            ]
                    except Exception as e:
                        logger.warning(f"Error extracting selector {css_selector}: {e}")
                        scraped_data[field_name] = None
                
                logger.info(f"Successfully scraped {url} with Playwright")
                return scraped_data
                
        except ImportError:
            logger.error("Playwright not installed")
            raise Exception("Playwright not installed. Run: pip install playwright && playwright install chromium")
        except Exception as e:
            logger.error(f"Error scraping {url} with Playwright: {e}")
            raise Exception(f"Failed to scrape website: {str(e)}")

    def _flatten_data(self, data: dict) -> list:
        """Flatten scraped data for counting items"""
        items = []
        for key, value in data.items():
            if isinstance(value, list):
                items.extend(value)
            elif value is not None:
                items.append(value)
        return items
    
    def _calculate_next_run(self, schedule: str) -> Optional[datetime]:
        """Calculate next run time based on schedule"""
        if schedule == "manual":
            return None
        
        now = datetime.now(timezone.utc)
        
        if schedule == "hourly":
            return now + timedelta(hours=1)
        elif schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        elif schedule == "monthly":
            return now + timedelta(days=30)
        else:
            return None
    
    async def get_jobs_due_for_run(self) -> List[Dict]:
        """Get all jobs that are due to run (for scheduled execution)"""
        try:
            now = datetime.now(timezone.utc)
            
            jobs = await self.scraping_jobs_collection.find({
                "enabled": True,
                "schedule": {"$ne": "manual"},
                "next_run": {"$lte": now}
            }).to_list(100)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting jobs due for run: {e}")
            raise
    
    async def toggle_job(self, job_id: str, user_id: str, enabled: bool) -> dict:
        """Enable or disable a scraping job"""
        try:
            job = await self.scraping_jobs_collection.find_one({
                "job_id": job_id,
                "user_id": ObjectId(user_id)
            })
            
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scraping job not found"
                )
            
            await self.scraping_jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": {"enabled": enabled}}
            )
            
            logger.info(f"Scraping job {job_id} {'enabled' if enabled else 'disabled'}")
            
            return {
                "job_id": job_id,
                "enabled": enabled,
                "message": f"Job {'enabled' if enabled else 'disabled'} successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error toggling scraping job: {e}")
            raise
    
    async def get_scraping_stats(self, user_id: str) -> dict:
        """Get comprehensive scraping statistics"""
        try:
            pipeline = [
                {"$match": {"user_id": ObjectId(user_id)}},
                {
                    "$group": {
                        "_id": None,
                        "total_jobs": {"$sum": 1},
                        "active_jobs": {
                            "$sum": {"$cond": [{"$eq": ["$enabled", True]}, 1, 0]}
                        },
                        "total_runs": {"$sum": "$run_count"},
                        "total_successes": {"$sum": "$success_count"},
                        "total_errors": {"$sum": "$error_count"}
                    }
                }
            ]
            
            result = await self.scraping_jobs_collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return {
                    "total_jobs": 0,
                    "active_jobs": 0,
                    "total_runs": 0,
                    "total_successes": 0,
                    "total_errors": 0,
                    "success_rate": 0
                }
            
            stats = result[0]
            success_rate = (
                (stats["total_successes"] / stats["total_runs"] * 100)
                if stats["total_runs"] > 0
                else 0
            )
            
            return {
                "total_jobs": stats["total_jobs"],
                "active_jobs": stats["active_jobs"],
                "total_runs": stats["total_runs"],
                "total_successes": stats["total_successes"],
                "total_errors": stats["total_errors"],
                "success_rate": round(success_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting scraping stats: {e}")
            raise
