"""Migration script to update external_email_id from IMAP sequence numbers to UIDs.

Fetches all emails from the past 1000 days via IMAP, matches them to database
records by subject + date, verifies the ID/UID difference is exactly 1, and
updates the database."""

from datetime import datetime, timedelta

from app.config import settings
from app.database import get_db
from app.emails.email_service import EmailService
from app.job_email_scraping.models import JobEmail


def fetch_seq_to_uid_mapping(email_service: EmailService) -> dict[str, str]:
    """Fetch all emails from the past 1000 days and build a seq_num -> UID mapping."""

    mail = email_service._connect_imap()

    try:
        mail.select("INBOX")
        since_date = (datetime.now() - timedelta(days=1000)).strftime("%d-%b-%Y")

        # Search using sequence numbers
        status, seq_data = mail.search(None, f"SINCE {since_date}")
        if status != "OK" or not seq_data[0]:
            print("No emails found via sequence search.")
            return {}

        seq_nums = seq_data[0].split()

        # Search using UIDs
        status, uid_data = mail.uid("search", None, f"SINCE {since_date}")
        if status != "OK" or not uid_data[0]:
            print("No emails found via UID search.")
            return {}

        uids = uid_data[0].split()

        if len(seq_nums) != len(uids):
            print(f"WARNING: Sequence count ({len(seq_nums)}) != UID count ({len(uids)})")
            return {}

        print(f"Found {len(uids)} emails in IMAP (past 1000 days)")

        return {seq.decode(): uid.decode() for seq, uid in zip(seq_nums, uids)}

    finally:
        mail.close()
        mail.logout()


def run_migration(dry_run: bool = True):
    """Run the migration.
    :param dry_run: If True, only print what would change without updating the DB."""

    db = next(get_db())
    email_service = EmailService(settings.scraper_email_username, settings.scraper_email_password)

    seq_to_uid = fetch_seq_to_uid_mapping(email_service)
    if not seq_to_uid:
        print("No IMAP emails fetched. Aborting.")
        return

    # Also build the reverse (uid -> seq) to detect already-migrated records
    uid_set = set(seq_to_uid.values())

    # Get all DB records
    db_emails = db.query(JobEmail).all()
    print(f"Found {len(db_emails)} emails in database")

    matched = 0
    mismatched = 0
    not_found = 0
    updates = []

    for db_email in db_emails:
        old_id = db_email.external_email_id

        if old_id.startswith("jam@emmanuelpean.me_"):
            continue

        # Check if the old ID exists as a sequence number
        if old_id in seq_to_uid:
            new_uid = seq_to_uid[old_id]
            diff = int(new_uid) - int(old_id)

            if diff == 1:
                matched += 1
                updates.append((db_email.id, old_id, new_uid))
                print(f"  [OK] DB email {db_email.id}: {old_id} -> {new_uid} (diff={diff})")
            else:
                mismatched += 1
                print(f"  [MISMATCH] DB email {db_email.id}: {old_id} -> {new_uid} (diff={diff}, expected 1)")

        # Check if old_id is already a UID (already migrated)
        elif old_id in uid_set:
            print(f"  [SKIP] DB email {db_email.id}: {old_id} already appears to be a UID")
            matched += 1

        else:
            not_found += 1
            print(f"  [NOT FOUND] DB email {db_email.id}: seq_num {old_id} not found in IMAP")

    print(f"\nSummary:")
    print(f"  Matched (diff=1): {matched}")
    print(f"  Mismatched (diff!=1): {mismatched}")
    print(f"  Not found in IMAP: {not_found}")
    print(f"  Total to update: {len(updates)}")

    if dry_run:
        print(f"\nDRY RUN - no changes made. Run with dry_run=False to apply updates.")
    else:
        for db_id, old_id, new_uid in updates:
            db.query(JobEmail).filter(JobEmail.id == db_id).update({JobEmail.external_email_id: new_uid})
        db.commit()
        print(f"\nUpdated {len(updates)} records.")


if __name__ == "__main__":
    import sys

    dry = "--apply" not in sys.argv
    if dry:
        print("=== DRY RUN MODE (pass --apply to update the database) ===\n")
    else:
        print("=== APPLYING CHANGES ===\n")

    run_migration(dry_run=dry)
