import asyncio
from typing import Optional, Dict, List, Any
from aiohttp import ClientSession, TCPConnector, ClientError, ClientTimeout
from bs4 import BeautifulSoup
import json
import random
from app.core.logging import logger
from datetime import datetime, timezone


class ScraperClient:
    """Base class for web scraping with async support and anti-blocking measures"""
    
    # List of realistic User-Agents to rotate
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    ]
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict] = None, use_rotating_ua: bool = True):
        """
        Initialize scraper client with anti-blocking measures
        
        Args:
            timeout: Request timeout in seconds
            headers: Custom headers for requests
            use_rotating_ua: Whether to rotate User-Agent strings
        """
        self.timeout = timeout
        self.use_rotating_ua = use_rotating_ua
        self.session: Optional[ClientSession] = None
        
        # Comprehensive headers to avoid bot detection
        self.default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }
        
        if headers:
            self.default_headers.update(headers)
    
    def _get_headers(self, url: str) -> Dict[str, str]:
        """Generate headers with rotating User-Agent"""
        headers = self.default_headers.copy()
        
        if self.use_rotating_ua:
            headers['User-Agent'] = random.choice(self.USER_AGENTS)
        else:
            headers['User-Agent'] = self.USER_AGENTS[0]
        
        # Set referer based on domain
        domain = url.split('/')[2] if len(url.split('/')) > 2 else ''
        headers['Referer'] = f'https://www.google.com/search?q={domain}'
        
        return headers
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = TCPConnector(
            limit_per_host=3,  # Reduced to be gentler
            enable_cleanup_closed=True,
            force_close=True,
        )
        timeout = ClientTimeout(total=self.timeout)
        self.session = ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Adding delay of {delay:.2f} seconds")
        await asyncio.sleep(delay)
    
    async def fetch_html(
        self, 
        url: str, 
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic
        
        Args:
            url: Target URL
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
        
        Returns:
            HTML content or None if failed
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        
        # Add random delay before request
        await self._random_delay()
        
        headers = self._get_headers(url)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
                
                async with self.session.get(
                    url,
                    headers=headers,
                    allow_redirects=True,
                    ssl=True
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"Successfully fetched {url} ({len(html)} bytes)")
                        return html
                    
                    elif response.status == 403:
                        logger.error(f"403 Forbidden - {url} is blocking scrapers. Headers may need update.")
                        # Try with different User-Agent on next attempt
                        headers = self._get_headers(url)
                    
                    elif response.status == 429:
                        retry_after = response.headers.get('Retry-After', retry_delay * (2 ** attempt))
                        logger.warning(f"429 Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(float(retry_after))
                    
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {url} (attempt {attempt + 1})")
            
            except ClientError as e:
                logger.error(f"Client error fetching {url}: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
            
            # Exponential backoff before retry
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                # Rotate headers for next attempt
                headers = self._get_headers(url)
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    async def fetch_json(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Fetch and parse JSON from URL"""
        html = await self.fetch_html(url, max_retries)
        if html:
            try:
                return json.loads(html)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from {url}")
        return None
    
    def parse_html(self, html: str, parser: str = 'html.parser') -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, parser)


class StealthScraper(ScraperClient):
    """Advanced scraper with additional stealth measures"""
    
    async def fetch_with_stealth(self, url: str) -> Optional[str]:
        """Fetch with maximum stealth measures"""
        # Longer random delay
        await self._random_delay(2.0, 5.0)
        
        # Add more realistic headers
        headers = self._get_headers(url)
        headers.update({
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        
        return await self.fetch_html(url, max_retries=5, retry_delay=3.0)


class PlaywrightScraper:
    """Headless browser scraper using Playwright for JavaScript-heavy sites"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML using Playwright headless browser"""
        try:
            from playwright.async_api import async_playwright
            
            logger.info(f"Fetching {url} using Playwright headless browser")
            
            async with async_playwright() as p:
                # Launch browser with stealth options
                browser = await p.chromium.launch(
                    headless=self.headless,
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
                    geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
                    permissions=['geolocation'],
                    color_scheme='light',
                    reduced_motion='no-preference',
                )
                
                page = await context.new_page()
                
                # Set extra HTTP headers
                await page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.google.com/',
                    'DNT': '1',
                })
                
                # Navigate to page with wait
                response = await page.goto(
                    url,
                    wait_until='networkidle',
                    timeout=self.timeout * 1000
                )
                
                if response.status == 403:
                    logger.error(f"Playwright: 403 Forbidden from {url}")
                    await browser.close()
                    return None
                
                # Additional wait for JavaScript rendering
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(2)  # Extra delay for dynamic content
                
                # Get page content
                html = await page.content()
                
                await browser.close()
                
                logger.info(f"Successfully fetched {url} using Playwright ({len(html)} bytes)")
                return html
                
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
            return None
        except Exception as e:
            logger.error(f"Playwright error fetching {url}: {e}")
            return None
    
    async def smart_fetch(self, url: str) -> Optional[str]:
        """
        Smart fetch: Try aiohttp first, fallback to Playwright on 403/blocking
        """
        # First try with standard ScraperClient
        async with ScraperClient(use_rotating_ua=True) as scraper:
            html = await scraper.fetch_html(url, max_retries=2)
            if html:
                return html
        
        # If standard failed, try StealthScraper
        logger.info(f"Standard scraper failed for {url}, trying StealthScraper...")
        async with StealthScraper() as scraper:
            html = await scraper.fetch_with_stealth(url)
            if html:
                return html
        
        # If still blocked, fallback to Playwright
        logger.info(f"Stealth scraper failed for {url}, trying Playwright headless browser...")
        return await self.fetch_html(url)


# Backward compatibility classes
class WebPageScraper(ScraperClient):
    """Backward compatible web page scraper"""
    
    async def scrape_page(self, url: str) -> Optional[str]:
        """Scrape a single web page"""
        return await self.fetch_html(url)


class APIScraper(ScraperClient):
    """Backward compatible API scraper"""
    
    async def fetch_api(self, url: str) -> Optional[Dict]:
        """Fetch JSON from API endpoint"""
        return await self.fetch_json(url)
