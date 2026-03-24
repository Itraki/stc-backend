import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """Middleware to rotate User-Agent strings"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent
        return None


class CustomRetryMiddleware(RetryMiddleware):
    """Custom retry middleware with better handling for bot protection"""
    
    EXCEPTIONS_TO_RETRY = (
        TimeoutError, 
        TCPTimedOutError, 
        ConnectionRefusedError, 
        TunnelError,
    )
    
    def __init__(self, settings):
        super().__init__(settings)
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.retry_times = settings.getint('RETRY_TIMES')
        
    def process_response(self, request, response, spider):
        # Check if we should retry
        if response.status == 403:
            spider.logger.warning(f"403 Forbidden - {request.url}. Will use Playwright.")
            # Let Playwright handle 403s
            return response
            
        return super().process_response(request, response, spider)
    
    def process_exception(self, request, exception, spider):
        spider.logger.warning(f"Exception {exception} for {request.url}")
        return super().process_exception(request, exception, spider)
