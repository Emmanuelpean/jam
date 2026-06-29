"""Migration script to update external_email_id from IMAP sequence numbers to UIDs.

Fetches all emails from the past 1000 days via IMAP, matches them to database
records by subject + date_received, and updates the database.
Multiple IMAP matches for a single DB record are highlighted as ambiguous.
"""

import sys

from app.config import settings
from app.database import db_session
from app.emails.email_service import EmailService
from app.job_email_scraping.models import JobEmail


def run_migration(dry_run: bool = True):
    """Run the migration.
    :param dry_run: If True, only print what would change without updating the DB."""

    with db_session() as db:
        email_service = EmailService(settings.scraper_email_username, settings.scraper_email_password)

        vps_emails = email_service.get_emails(timedelta_days=10000)
        emails_db = db.query(JobEmail).order_by(JobEmail.external_email_id).all()
        emails_db = [email for email in emails_db if not email.external_email_id.startswith("jam")]
        emails_db = sorted(emails_db, key=lambda email: int(email.external_email_id))

        for email_db in emails_db[::-1]:
            matching = [
                vps_email
                for vps_email in vps_emails
                if vps_email.date == email_db.date_received and vps_email.subject == email_db.subject
            ]
            if len(matching) != 1:
                raise AssertionError(f"Should be 1, Is {len(matching)}")
            print(
                f"Current external_email_id is {email_db.external_email_id}, new UID is {matching[0].id}. "
                f"Difference is {int(email_db.external_email_id) - int(matching[0].id)}"
            )
            if dry_run:
                pass
            else:
                email_db.external_email_id = matching[0].id
            db.commit()


if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    if dry:
        print("=== DRY RUN MODE (pass --apply to update the database) ===\n")
    else:
        print("=== APPLYING CHANGES ===\n")

    run_migration(dry_run=dry)
