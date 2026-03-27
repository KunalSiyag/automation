"""
Tests for web scraper.
"""

import pytest
from scraper import URLValidator, RateLimiter, HTMLParser, Scraper


def test_url_validator_valid():
    """Test URL validation."""
    assert URLValidator.is_valid_url("https://example.com")
    assert URLValidator.is_valid_url("http://example.com/path")
    assert URLValidator.is_valid_url("https://sub.example.com:8080")


def test_url_validator_invalid():
    """Test invalid URLs."""
    assert not URLValidator.is_valid_url("not a url")
    assert not URLValidator.is_valid_url("example.com")


def test_url_validator_normalize():
    """Test URL normalization."""
    normalized = URLValidator.normalize_url("example.com")
    assert normalized.startswith("https://")


def test_html_parser_extract_links():
    """Test extracting links."""
    html = '<a href="https://example.com">link</a><a href="https://test.com">test</a>'
    links = HTMLParser.extract_links(html)
    assert len(links) == 2
    assert "https://example.com" in links


def test_html_parser_extract_text():
    """Test extracting text."""
    html = "<p>Hello <b>World</b></p>"
    text = HTMLParser.extract_text(html)
    assert "Hello" in text
    assert "World" in text
    assert "<" not in text


def test_html_parser_extract_headings():
    """Test extracting headings."""
    html = "<h1>Main Title</h1><h2>Subtitle</h2>"
    headings = HTMLParser.extract_headings(html)
    assert len(headings) == 2
    assert "Main Title" in headings


def test_html_parser_extract_images():
    """Test extracting images."""
    html = '<img src="https://example.com/img1.jpg"/><img src="https://example.com/img2.png"/>'
    images = HTMLParser.extract_images(html)
    assert len(images) == 2
    assert "https://example.com/img1.jpg" in images


def test_scraper_visited():
    """Test visited URL tracking."""
    scraper = Scraper()
    url = "https://example.com"
    assert not scraper.has_visited(url)
    scraper.mark_visited(url)
    assert scraper.has_visited(url)


def test_scraper_extract_data():
    """Test data extraction."""
    scraper = Scraper()
    html = """
    <h1>Title</h1>
    <a href="https://link.com">Link</a>
    <img src="https://img.com/pic.jpg"/>
    <p>Some text here</p>
    """
    
    selectors = {
        'headings': True,
        'links': True,
        'images': True,
        'text': True,
    }
    
    data = scraper.extract_data(html, selectors)
    assert 'headings' in data
    assert len(data['headings']) > 0
    assert 'links' in data
    assert len(data['links']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
