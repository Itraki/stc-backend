import scrapy
from scrapy_playwright.page import PageMethod
from typing import Optional, Dict
import json
from datetime import datetime


class GenericWebSpider(scrapy.Spider):
    """
    Generic web spider using Scrapy + Playwright
    Can scrape any URL with JavaScript rendering
    """
    
    name = "generic_web"
    
    def __init__(self, url: str = None, selectors: Dict[str, str] = None, **kwargs):
        super().__init__(**kwargs)
        self.start_url = url
        self.selectors = selectors or {}
        self.results = {}
        
    def start_requests(self):
        if not self.start_url:
            self.logger.error("No URL provided")
            return
            
        self.logger.info(f"Starting to scrape: {self.start_url}")
        
        yield scrapy.Request(
            self.start_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    # Wait for page to load
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    # Wait for network to be idle
                    PageMethod("wait_for_load_state", "networkidle"),
                    # Scroll to bottom to trigger lazy loading
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    # Wait a bit for any dynamic content
                    PageMethod("wait_for_timeout", 2000),
                ],
                "playwright_context_kwargs": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-US",
                },
            },
            callback=self.parse,
        )
    
    def parse(self, response):
        """Parse the page using CSS selectors"""
        self.logger.info(f"Successfully fetched {response.url}")
        
        data = {
            "url": response.url,
            "status": response.status,
            "timestamp": datetime.utcnow().isoformat(),
            "title": response.css("title::text").get(),
            "scraped_data": {}
        }
        
        # Extract data using selectors
        for field_name, css_selector in self.selectors.items():
            try:
                elements = response.css(css_selector)
                
                if len(elements) == 1:
                    # Single element
                    text = elements.css("::text").get()
                    data["scraped_data"][field_name] = text.strip() if text else None
                elif len(elements) > 1:
                    # Multiple elements
                    texts = elements.css("::text").getall()
                    data["scraped_data"][field_name] = [t.strip() for t in texts if t.strip()]
                else:
                    data["scraped_data"][field_name] = None
                    
            except Exception as e:
                self.logger.warning(f"Error extracting {field_name}: {e}")
                data["scraped_data"][field_name] = None
        
        # Store results
        self.results = data
        yield data


class UNICEFSpider(GenericWebSpider):
    """Specialized spider for UNICEF websites"""
    
    name = "unicef"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def start_requests(self):
        if not self.start_url:
            return
            
        self.logger.info(f"Starting UNICEF scrape: {self.start_url}")
        
        # Extra measures for UNICEF's strong bot protection
        yield scrapy.Request(
            self.start_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    # Wait longer for UNICEF
                    PageMethod("wait_for_load_state", "domcontentloaded"),
                    PageMethod("wait_for_load_state", "networkidle"),
                    # Simulate human-like scrolling
                    PageMethod("evaluate", """
                        async () => {
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            window.scrollTo(0, document.body.scrollHeight / 2);
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            window.scrollTo(0, document.body.scrollHeight);
                            await new Promise(resolve => setTimeout(resolve, 1000));
                        }
                    """),
                    PageMethod("wait_for_timeout", 3000),
                ],
                "playwright_context_kwargs": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-US",
                    "timezone_id": "America/New_York",
                    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
                    "permissions": ["geolocation"],
                },
                # Use stealth mode
                "playwright_include_page": True,
            },
            callback=self.parse,
            errback=self.handle_error,
        )
    
    def handle_error(self, failure):
        """Handle request errors"""
        self.logger.error(f"Request failed: {failure.getErrorMessage()}")
        yield {
            "url": self.start_url,
            "status": "failed",
            "error": str(failure.getErrorMessage()),
            "timestamp": datetime.utcnow().isoformat(),
        }
