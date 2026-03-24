from datetime import datetime, timezone
from typing import Optional


class ScrapedDataPipeline:
    """Pipeline to process and store scraped data"""
    
    def process_item(self, item, spider):
        """Process each scraped item"""
        spider.logger.info(f"Processing scraped data from {item.get('url')}")
        
        # Add metadata
        item['processed_at'] = datetime.utcnow().isoformat()
        item['spider_name'] = spider.name
        
        # Clean and validate data
        if item.get('scraped_data'):
            for key, value in item['scraped_data'].items():
                if isinstance(value, str):
                    item['scraped_data'][key] = value.strip()
        
        return item
    
    def open_spider(self, spider):
        spider.logger.info(f"Pipeline opened for spider: {spider.name}")
    
    def close_spider(self, spider):
        spider.logger.info(f"Pipeline closed for spider: {spider.name}")
