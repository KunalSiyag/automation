"""
Web scraping utilities and fetchers.
"""

import time
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse
import re


class URLValidator:
    """Validate and normalize URLs."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class RateLimiter:
    """Rate limiter for requests."""
    
    def __init__(self, min_delay: float = 1.0):
        """Initialize rate limiter."""
        self.min_delay = min_delay
        self.last_request_time = 0
    
    def wait(self):
        """Wait before making next request."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()


class HTMLParser:
    """Basic HTML parsing utilities."""
    
    @staticmethod
    def extract_links(html: str) -> List[str]:
        """Extract all links from HTML."""
        link_pattern = r'href=["\'](https?://[^\s"\'<>]+)'
        return re.findall(link_pattern, html)
    
    @staticmethod
    def extract_text(html: str) -> str:
        """Extract plain text from HTML."""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remove HTML tags
        html = re.sub(r'<[^>]+>', ' ', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', html).strip()
        return text
    
    @staticmethod
    def extract_headings(html: str) -> List[str]:
        """Extract all headings from HTML."""
        headings = []
        for match in re.finditer(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', html, re.IGNORECASE):
            headings.append(match.group(1))
        return headings
    
    @staticmethod
    def extract_images(html: str) -> List[str]:
        """Extract image URLs from HTML."""
        img_pattern = r'src=["\'](https?://[^\s"\'<>]+)'
        return re.findall(img_pattern, html)


class Scraper:
    """Web scraper with safety features."""
    
    def __init__(self, rate_limit: float = 1.0):
        """Initialize scraper."""
        self.rate_limiter = RateLimiter(rate_limit)
        self.visited_urls: set = set()
    
    def has_visited(self, url: str) -> bool:
        """Check if URL has been visited."""
        return url in self.visited_urls
    
    def mark_visited(self, url: str):
        """Mark URL as visited."""
        self.visited_urls.add(url)
    
    def extract_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract data from HTML using simple selectors."""
        data = {}
        
        if 'links' in selectors:
            data['links'] = HTMLParser.extract_links(html)
        
        if 'text' in selectors:
            data['text'] = HTMLParser.extract_text(html)
        
        if 'headings' in selectors:
            data['headings'] = HTMLParser.extract_headings(html)
        
        if 'images' in selectors:
            data['images'] = HTMLParser.extract_images(html)
        
        return data
