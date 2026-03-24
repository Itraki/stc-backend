# Scrapy settings for STC Backend

BOT_NAME = 'stc_scraper'

SPIDER_MODULES = ['app.scrapy_spiders.spiders']
NEWSPIDER_MODULE = 'app.scrapy_spiders.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Set to True for production

# Configure Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--disable-gpu",
        "--hide-scrollbars",
        "--mute-audio",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-extensions",
    ]
}

# User-Agent rotation
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Download settings
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 3
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 500, 502, 503, 504]

# Logging
LOG_LEVEL = 'INFO'

# Pipelines
ITEM_PIPELINES = {
    'app.scrapy_spiders.pipelines.ScrapedDataPipeline': 300,
}

# Request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Spider middlewares
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
}

# Downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'app.scrapy_spiders.middlewares.RotateUserAgentMiddleware': 110,
    'app.scrapy_spiders.middlewares.CustomRetryMiddleware': 120,
}

# Cache
HTTPCACHE_ENABLED = False  # Enable for development
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
