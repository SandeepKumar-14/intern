import logging

import requests
from bs4 import BeautifulSoup

from config import Config

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ScheduledScraperBot/1.0; "
        "+https://example.com/bot)"
    )
}


def scrape_static(url: str, css_selector: str | None = None) -> list[dict]:
    """Fetch a static page and extract items matching css_selector."""
    response = requests.get(url, headers=HEADERS, timeout=Config.REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    selector = css_selector or "body"
    nodes = soup.select(selector)

    items = []
    for node in nodes:
        link = node.find("a")
        items.append(
            {
                "title": node.get_text(strip=True)[:1024],
                "content": str(node)[:5000],
                "url": link["href"] if link and link.has_attr("href") else url,
            }
        )
    logger.info("Static scrape of %s found %d items", url, len(items))
    return items
