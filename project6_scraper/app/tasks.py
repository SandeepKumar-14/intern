import csv
import logging
import os
from datetime import datetime

from .celery_app import celery_app
from .models import SessionLocal, ScrapeTarget, ScrapedItem, init_db
from .scrapers.static_scraper import scrape_static
from .scrapers.dynamic_scraper import scrape_dynamic
from config import Config

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scrape_target", bind=True, max_retries=3, default_retry_delay=60)
def scrape_target(self, target_id: int):
    session = SessionLocal()
    try:
        target = session.get(ScrapeTarget, target_id)
        if target is None:
            logger.warning("Target %s not found", target_id)
            return {"target_id": target_id, "items": 0}

        try:
            if target.use_selenium:
                raw_items = scrape_dynamic(target.url, target.css_selector)
            else:
                raw_items = scrape_static(target.url, target.css_selector)
        except Exception as exc:
            logger.exception("Scrape failed for target %s", target_id)
            raise self.retry(exc=exc)

        for item in raw_items:
            session.add(
                ScrapedItem(
                    target_id=target.id,
                    title=item.get("title"),
                    content=item.get("content"),
                    url=item.get("url"),
                )
            )
        session.commit()
        logger.info("Stored %d items for target %s", len(raw_items), target_id)
        return {"target_id": target_id, "items": len(raw_items)}
    finally:
        session.close()


@celery_app.task(name="app.tasks.scrape_all_targets")
def scrape_all_targets():
    session = SessionLocal()
    try:
        target_ids = [t.id for t in session.query(ScrapeTarget).all()]
    finally:
        session.close()

    for tid in target_ids:
        scrape_target.delay(tid)

    return {"queued_targets": len(target_ids)}


@celery_app.task(name="app.tasks.export_to_csv")
def export_to_csv(target_id: int | None = None):
    session = SessionLocal()
    try:
        query = session.query(ScrapedItem)
        if target_id is not None:
            query = query.filter(ScrapedItem.target_id == target_id)
        items = query.all()

        os.makedirs(Config.EXPORT_DIR, exist_ok=True)
        filename = f"export_{target_id or 'all'}_{datetime.utcnow():%Y%m%d_%H%M%S}.csv"
        filepath = os.path.join(Config.EXPORT_DIR, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "target_id", "title", "url", "scraped_at"])
            for item in items:
                writer.writerow(
                    [item.id, item.target_id, item.title, item.url, item.scraped_at]
                )

        logger.info("Exported %d rows to %s", len(items), filepath)
        return {"file": filepath, "rows": len(items)}
    finally:
        session.close()


# Ensure tables exist when the worker starts.
init_db()
