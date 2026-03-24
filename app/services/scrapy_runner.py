"""
ScrapyRunner: runs Scrapy spiders programmatically inside the FastAPI async context.

Scrapy is configured to use the AsyncioSelectorReactor (see scrapy_spiders/settings.py),
which shares the same event loop as uvicorn/FastAPI. CrawlerRunner (not CrawlerProcess)
is used so it never stops the reactor — it just resolves a Deferred when the spider finishes.
"""
import asyncio
from typing import Dict, List, Optional
from app.core.logging import logger


class ScrapyRunner:
    """Runs Scrapy spiders from within the FastAPI async event loop."""

    _reactor_installed: bool = False

    @classmethod
    def _ensure_reactor(cls) -> bool:
        """Install the asyncio reactor if it hasn't been installed yet."""
        if cls._reactor_installed:
            return True
        try:
            import scrapy.utils.reactor as scrapy_reactor
            scrapy_reactor.install_reactor(
                "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
            )
            cls._reactor_installed = True
            logger.info("Asyncio reactor installed for Scrapy")
            return True
        except Exception as exc:
            logger.warning(f"Could not install asyncio reactor: {exc}")
            return False

    @classmethod
    async def run_generic_spider(cls, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """
        Run GenericWebSpider against *url* using *selectors*.

        Returns the first scraped item dict on success, or None on failure.
        The spider yields exactly one item per URL, so the first element is the result.
        """
        if not cls._ensure_reactor():
            return None

        try:
            from scrapy.crawler import CrawlerRunner
            from scrapy.settings import Settings
            from scrapy import signals
            from app.scrapy_spiders.spiders.generic_web import GenericWebSpider
            import app.scrapy_spiders.settings as spider_settings_module

            scrapy_settings = Settings()
            scrapy_settings.setmodule(spider_settings_module)

            runner = CrawlerRunner(scrapy_settings)
            collected: List[Dict] = []

            crawler = runner.create_crawler(GenericWebSpider)

            def _on_item_scraped(item, response, spider):  # noqa: ARG001
                collected.append(dict(item))

            crawler.signals.connect(_on_item_scraped, signal=signals.item_scraped)

            d = runner.crawl(crawler, url=url, selectors=selectors)
            # Convert Twisted Deferred → asyncio Future so we can await it.
            # defer.ensureDeferred() does not work here because d is already
            # a Deferred (not a coroutine); asFuture() is the correct bridge.
            loop = asyncio.get_running_loop()
            await d.asFuture(loop)

            return collected[0] if collected else None

        except Exception as exc:
            logger.error(f"ScrapyRunner error for {url}: {exc}")
            return None
