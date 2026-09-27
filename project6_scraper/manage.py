import argparse

from app.models import init_db, SessionLocal, ScrapeTarget
from app.tasks import scrape_target, scrape_all_targets, export_to_csv


def add_target(args):
    init_db()
    session = SessionLocal()
    try:
        target = ScrapeTarget(
            name=args.name,
            url=args.url,
            css_selector=args.selector,
            use_selenium=1 if args.selenium else 0,
        )
        session.add(target)
        session.commit()
        print(f"Added target {target.id}: {target.name} ({target.url})")
    finally:
        session.close()


def run_now(args):
    if args.target_id:
        result = scrape_target.apply_async(args=[args.target_id])
    else:
        result = scrape_all_targets.apply_async()
    print(f"Queued task: {result.id}")


def export(args):
    result = export_to_csv.apply_async(args=[args.target_id])
    print(f"Queued export task: {result.id}")


def list_targets(_args):
    init_db()
    session = SessionLocal()
    try:
        for t in session.query(ScrapeTarget).all():
            print(f"[{t.id}] {t.name} -> {t.url} (selenium={bool(t.use_selenium)})")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Manage scrape targets and jobs")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add-target", help="Register a new scrape target")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--url", required=True)
    p_add.add_argument("--selector", default=None)
    p_add.add_argument("--selenium", action="store_true")
    p_add.set_defaults(func=add_target)

    p_list = sub.add_parser("list-targets", help="List registered targets")
    p_list.set_defaults(func=list_targets)

    p_run = sub.add_parser("run-now", help="Trigger a scrape immediately")
    p_run.add_argument("--target-id", type=int, default=None)
    p_run.set_defaults(func=run_now)

    p_export = sub.add_parser("export", help="Export scraped items to CSV")
    p_export.add_argument("--target-id", type=int, default=None)
    p_export.set_defaults(func=export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
