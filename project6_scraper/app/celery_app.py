from celery import Celery
from celery.schedules import crontab

from config import Config

celery_app = Celery(
    "scraper",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "scrape-all-targets-periodic": {
        "task": "app.tasks.scrape_all_targets",
        "schedule": Config.SCRAPE_INTERVAL_MINUTES * 60,
    },
}
