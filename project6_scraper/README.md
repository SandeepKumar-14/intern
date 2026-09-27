# Automated Web Scraper with Scheduler

Scrapes static pages (requests + BeautifulSoup) or JS-rendered pages
(Selenium), stores results in SQLite via SQLAlchemy, runs on a schedule with
Celery Beat, and exports to CSV.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # then edit values
```

You'll need Redis running locally (used as Celery broker/backend):

```bash
docker run -p 6379:6379 redis:7
```

For Selenium (dynamic scraping) you'll also need Chrome/Chromium and a
matching `chromedriver` on your PATH.

## Usage

Register a target to scrape:

```bash
python manage.py add-target --name "Example News" --url "https://example.com/news" \
    --selector "div.article" 
```

Add `--selenium` for JS-rendered pages.

List targets:

```bash
python manage.py list-targets
```

Start the Celery worker and beat scheduler (two terminals):

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
celery -A app.celery_app.celery_app beat --loglevel=info
```

Trigger an immediate scrape (all targets, or one target by id):

```bash
python manage.py run-now
python manage.py run-now --target-id 1
```

Export scraped data to CSV:

```bash
python manage.py export --target-id 1
```

Files land in the `exports/` directory.

## Schedule

The interval is controlled by `SCRAPE_INTERVAL_MINUTES` in `.env` (default
60). Celery Beat picks it up from `app/celery_app.py`'s `beat_schedule`.

## Tests

```bash
pytest
```
