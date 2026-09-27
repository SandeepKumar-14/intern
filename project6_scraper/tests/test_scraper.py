from unittest.mock import patch, MagicMock

from app.scrapers.static_scraper import scrape_static


@patch("app.scrapers.static_scraper.requests.get")
def test_scrape_static_extracts_items(mock_get):
    mock_response = MagicMock()
    mock_response.text = (
        "<html><body>"
        "<div class='item'><a href='/one'>First</a></div>"
        "<div class='item'><a href='/two'>Second</a></div>"
        "</body></html>"
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    items = scrape_static("https://example.com", css_selector="div.item")

    assert len(items) == 2
    assert items[0]["title"] == "First"
    assert items[0]["url"] == "/one"


@patch("app.scrapers.static_scraper.requests.get")
def test_scrape_static_defaults_to_page_url_when_no_link(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html><body><div class='item'>No link here</div></body></html>"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    items = scrape_static("https://example.com", css_selector="div.item")

    assert items[0]["url"] == "https://example.com"
