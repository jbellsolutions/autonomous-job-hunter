"""AI Integraterz Autonomous Job Agent — main entry point.

Scrapes Upwork and OnlineJobs.ph for recent AI automation jobs, generates
a personalized application for each using Gemini, and writes results to CSV.

Usage:
    python run.py                        # all platforms
    python run.py --platform upwork      # just upwork
    python run.py --smoke-test           # headless, 1 job per platform, stub Gemini
    python run.py --max 5                # override drafts_per_run
"""
import argparse
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

# Force UTF-8 output on Windows so unicode arrows/em-dashes don't crash the run.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent
ENV_PATH = REPO_ROOT / ".env"
CONFIG_PATH = REPO_ROOT / "config.json"

PLATFORM_LABELS = {
    "upwork": "Upwork",
    "onlinejobs": "OnlineJobs.ph",
}


def load_config():
    if not ENV_PATH.exists() or not CONFIG_PATH.exists():
        print("Missing .env or config.json. Run: python setup.py")
        sys.exit(1)
    load_dotenv(ENV_PATH)
    if not os.environ.get("GOOGLE_API_KEY", "").strip():
        print("GOOGLE_API_KEY is empty. Run: python setup.py")
        sys.exit(1)
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"config.json is invalid: {e}. Run: python setup.py")
        sys.exit(1)
    return config


def day_number(config) -> int:
    try:
        start = date.fromisoformat(config.get("start_date", date.today().isoformat()))
    except Exception:
        start = date.today()
    return (date.today() - start).days + 1


def write_csv(path: Path, rows: list[dict]):
    fieldnames = ["date", "platform", "title", "link", "budget", "posted_date", "application_text"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main():
    parser = argparse.ArgumentParser(
        description="AI Integraterz Autonomous Job Agent"
    )
    parser.add_argument(
        "--platform",
        choices=["upwork", "onlinejobs", "all"],
        default="all",
        help="Which platform to scrape (default: all).",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Headless, 1 job per platform, stubbed Gemini output. For verification.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Override drafts_per_run from config.",
    )
    args = parser.parse_args()

    config = load_config()

    max_jobs = args.max if args.max is not None else config.get("drafts_per_run", 10)
    if args.smoke_test:
        max_jobs = 1

    platforms = ["upwork", "onlinejobs"] if args.platform == "all" else [args.platform]

    # Lazy imports so `--help` doesn't require selenium
    from scrapers.browser import get_driver

    print(f"\nStarting run (platforms: {', '.join(platforms)}, max/platform: {max_jobs})")
    if args.smoke_test:
        print("  [SMOKE TEST MODE — headless, Gemini stubbed]")

    driver = None
    all_rows: list[dict] = []
    per_platform_count: dict[str, int] = {}

    try:
        driver = get_driver(headless=args.smoke_test)

        for platform in platforms:
            print(f"\n→ Scraping {PLATFORM_LABELS[platform]}...")
            try:
                if platform == "upwork":
                    from scrapers.upwork import scrape as scrape_fn
                else:
                    from scrapers.onlinejobs import scrape as scrape_fn
                jobs = scrape_fn(driver, config, max_jobs=max_jobs)
            except Exception as e:
                print(f"  ! {platform} scrape failed: {e}")
                jobs = []

            platform_rows: list[dict] = []
            for job in jobs:
                if args.smoke_test:
                    application = "[SMOKE TEST STUB — Gemini not called]"
                else:
                    from scrapers.gemini import generate_application
                    print(f"  Drafting application for: {job['title'][:60]}...")
                    application = generate_application(
                        job["title"], job["description"], config
                    )

                row = {
                    "date": date.today().isoformat(),
                    "platform": PLATFORM_LABELS[platform],
                    "title": job["title"],
                    "link": job["link"],
                    "budget": job.get("budget", ""),
                    "posted_date": job.get("posted_date", ""),
                    "application_text": application,
                }
                platform_rows.append(row)

            # Per-platform CSV
            csv_path = REPO_ROOT / f"{platform}_drafts.csv"
            write_csv(csv_path, platform_rows)
            per_platform_count[platform] = len(platform_rows)
            all_rows.extend(platform_rows)
            print(f"  ✓ {len(platform_rows)} drafts → {csv_path.name}")

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Combined CSV
    combined = REPO_ROOT / "daily_drafts.csv"
    write_csv(combined, all_rows)

    # Summary
    total = len(all_rows)
    uw = per_platform_count.get("upwork", 0)
    ojp = per_platform_count.get("onlinejobs", 0)
    day = day_number(config)

    print("\n" + "=" * 60)
    print(f"  Drafted {total} applications.")
    print(f"     Upwork: {uw}   OnlineJobs.ph: {ojp}")
    print()
    print("  Next steps (Grad Playbook Part 6):")
    print("     1. Open daily_drafts.csv")
    print("     2. Review each — tweak the personalization line if needed")
    print("     3. Submit the 5-10 that look like a fit")
    print("     4. Log submissions in your tracking sheet")
    print("     5. Post your daily numbers in Skool")
    print()
    print("  Copy-paste for #grad-daily-standup:")
    print(
        f'     "Day {day} — Drafts ready: {total} ({uw} UW / {ojp} OJP). '
        f'Plan: submit 5, 50 emails, 15 DMs."'
    )
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(130)
