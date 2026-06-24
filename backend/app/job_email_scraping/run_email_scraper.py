"""CLI script to run the job email scraper once for a given number of days."""

import argparse
import sys

from app.job_email_scraping.email_scraper import JobEmailScrapingService
from app.job_email_scraping.schemas import JobEmailScrapingServiceLogOut


def main():
    """Run the job email scraper."""

    parser = argparse.ArgumentParser(description="Run the job email scraper for a specified number of days.")
    parser.add_argument(
        "--days",
        "-d",
        type=float,
        default=1,
        help="Number of days to look back for emails (default: 1)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.days <= 0:
        print("Error: days must be a positive number")
        sys.exit(1)

    print(f"Starting job email scraper for the last {args.days} day(s)...")

    scraper = JobEmailScrapingService()
    result = scraper.run_scraping(timedelta_days=args.days)

    if not JobEmailScrapingServiceLogOut.model_validate(result, from_attributes=True).is_success:
        print("\nError: scraping run failed — see the Error table for details")
        sys.exit(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
