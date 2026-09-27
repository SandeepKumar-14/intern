import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import Config

logger = logging.getLogger(__name__)


def _build_driver():
    options = Options()
    if Config.SELENIUM_HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (compatible; ScheduledScraperBot/1.0)"
    )
    return webdriver.Chrome(options=options)


def scrape_dynamic(url: str, css_selector: str | None = None, wait_seconds: int = 10) -> list[dict]:
    """Load a JS-rendered page with Selenium and extract items matching css_selector."""
    selector = css_selector or "body"
    driver = _build_driver()
    items = []
    try:
        driver.get(url)
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for el in elements:
            try:
                link_el = el.find_element(By.TAG_NAME, "a")
                href = link_el.get_attribute("href")
            except Exception:
                href = url

            items.append(
                {
                    "title": el.text.strip()[:1024],
                    "content": el.get_attribute("outerHTML")[:5000],
                    "url": href,
                }
            )
        logger.info("Dynamic scrape of %s found %d items", url, len(items))
    finally:
        driver.quit()

    return items
