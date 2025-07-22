"""Gmail Email Retrieval and LinkedIn Job Extraction Module

This module provides functionality to authenticate with Gmail using OAuth 2.0,
retrieve email messages, and extract LinkedIn job IDs from email content.
It offers a complete workflow for accessing Gmail data and parsing job-related
information from email bodies."""

import base64
import json
import os
import pickle
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from eis.job_scraper import LinkedinJobScraper, IndeedScrapper


class GmailRetriever:
    """Gmail Scrapper"""

    def __init__(
        self,
        token_file: str = "token.pickle",
        secrets_file: str = "eis_secrets.json",
    ) -> None:
        """Object constructor
        :param token_file: Path to the token pickle file
        :param secrets_file: Path to the secrets JSON file containing OAuth credentials
        """

        self.token_file = token_file
        self.secrets_file = secrets_file
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.service = None

        # Load credentials from the external file
        self.credentials_config = self._load_credentials()

        self.authenticate()

    def _load_credentials(self) -> dict:
        """Load OAuth credentials from secrets file"""
        try:
            with open(self.secrets_file, "r") as f:
                secrets = json.load(f)
                return secrets["google_auth"]  # Return the google_auth section, not the entire file
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Secrets file '{self.secrets_file}' not found. Please create it with your OAuth credentials."
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(
                f"Invalid JSON format in secrets file '{self.secrets_file}' or missing 'google_auth' section: {e}"
            )

    def authenticate(self) -> None:
        """Authenticate and create the Gmail service"""

        creds: Credentials | None = None

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(self.credentials_config, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, "wb") as token:
                # noinspection PyTypeChecker
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)

    def get_message_by_id(self, message_id: str) -> dict | None:
        """Retrieve a specific email by its message ID"""

        try:
            message = self.service.users().messages().get(userId="me", id=message_id, format="full").execute()
            return message
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def get_message_content(self, message_id: str) -> dict[str, str] | None:
        """Extract readable content from an email"""

        message = self.get_message_by_id(message_id)
        if not message:
            return None

        payload = message["payload"]
        headers = payload.get("headers", [])

        # Extract basic info
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

        # Extract body
        body = self._extract_body(payload)

        return {
            "id": message_id,
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body,
        }

    def _extract_body(self, payload: dict) -> str:
        """Extract email body from payload"""

        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"]["data"]
                    body = self._decode_base64(data)
                    break
                elif part["mimeType"] == "text/html":
                    data = part["body"]["data"]
                    body = self._decode_base64(data)
        else:
            if payload["mimeType"] == "text/plain":
                data = payload["body"]["data"]
                body = self._decode_base64(data)

        return body

    @staticmethod
    def _decode_base64(data: str) -> str:
        """Decode base64 URL-safe string"""

        return base64.urlsafe_b64decode(data).decode("utf-8")

    def search_messages(
        self,
        query: str = "",
        max_results: int = 10,
    ) -> list[str]:
        """Search for messages matching a query"""

        try:
            result = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()

            messages = result.get("messages", [])
            return [msg["id"] for msg in messages]
        except Exception as error:
            print(f"An error occurred: {error}")
            return []

    def extract_jobs(self, body):
        """Determine the origin of the email"""

        if "alert@indeed.com" in body.lower():
            jobs_ids = self.extract_indeed_job_ids(body)
            for job_id in jobs_ids:
                scraper = IndeedScrapper(job_id)
                job_data = scraper.scrape_job()
                print(job_data)
        else:
            jobs_ids = self.extract_linkedin_job_ids(body)
            for job_id in jobs_ids:
                scraper = LinkedinJobScraper(job_id)
                job_data = scraper.scrape_job()

    @staticmethod
    def extract_linkedin_job_ids(body: str) -> list[str]:
        """Extract LinkedIn job IDs from the email body"""

        pattern = r"linkedin\.com/(?:comm/)?jobs/view/(\d+)"

        # Find all matches
        job_ids = re.findall(pattern, body, re.IGNORECASE)

        # Remove duplicates while preserving order
        unique_job_ids = list(dict.fromkeys(job_ids))

        return unique_job_ids

    def save_email_to_db(self, email_data: dict, job_ids: list[str], session):
        """
        Save email and job IDs to database

        :param email_data: Dictionary containing email metadata
        :param job_ids: List of job IDs found in the email
        :param session: SQLAlchemy database session
        :return: JobEmails instance
        """
        from app.eis.models import JobEmails

        # Check if email already exists
        existing_email = session.query(JobEmails).filter(
            JobEmails.email_id == email_data["id"]
        ).first()

        if existing_email:
            # Update existing email with new job IDs if any
            existing_email.add_job_ids(job_ids)
            existing_email.processed = True
            session.commit()
            return existing_email

        # Create new email record
        email_record = JobEmails(
            email_id=email_data["id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            date_received=email_data["date"],
            platform="indeed" if "alert@indeed.com" in email_data["sender"] else "linkedin",
            job_ids=job_ids,
            processed=True,
            owner_id=1  # You'll need to set this to the actual user ID
        )

        session.add(email_record)
        session.commit()
        session.refresh(email_record)

        return email_record

    def process_and_save_emails(self, query: str = "from:alert@indeed.com", max_results: int = 10):
        """
        Process emails and save to database

        :param query: Gmail search query
        :param max_results: Maximum number of emails to process
        """
        from app.database import get_db
        from app.eis.models import JobEmails

        # Get database session
        db = next(get_db())

        try:
            # Get email IDs
            message_ids = self.search_messages(query, max_results)

            processed_count = 0
            for message_id in message_ids:
                # Get email content
                email_content = self.get_message_content(message_id)
                if not email_content:
                    continue

                # Extract job IDs
                if "alert@indeed.com" in email_content["sender"]:
                    job_ids = self.extract_indeed_job_ids(email_content["body"])
                else:
                    job_ids = self.extract_linkedin_job_ids(email_content["body"])

                # Save to database
                email_record = self.save_email_to_db(email_content, job_ids, db)

                print(f"Processed email: {email_record.subject}")
                print(f"Job IDs found: {job_ids}")
                print(f"Total job count: {email_record.job_count}")
                print("-" * 50)

                processed_count += 1

            print(f"Successfully processed {processed_count} emails")

        except Exception as e:
            print(f"Error processing emails: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def extract_indeed_job_ids(body: str) -> list[str]:
        """Extract Indeed job advertisement IDs from email body URLs
        :param body: Email body content as string
        :return: List of unique Indeed job advertisement IDs"""

        # Pattern to match both pagead and rc URLs
        pattern = r"https?://(?:uk\.)?indeed\.com/(?:pagead|rc)/clk/dl\?[^>\s]+"

        # Find all matches
        job_urls = re.findall(pattern, body, re.IGNORECASE)

        # Remove duplicates while preserving order
        job_urls = list(dict.fromkeys(job_urls))

        job_ids = []

        for url in job_urls:
            # Try to extract 'ad' parameter first (for pagead URLs)
            ad_match = re.search(r"[?&]ad=([^&>\s]+)", url, re.IGNORECASE)
            if ad_match:
                job_ids.append(ad_match.group(1))
                continue

            # Try to extract 'jk' parameter (for rc URLs)
            jk_match = re.search(r"[?&]jk=([^&>\s]+)", url, re.IGNORECASE)
            if jk_match:
                job_ids.append(jk_match.group(1))

        # Remove duplicates while preserving order
        unique_job_ids = list(dict.fromkeys(job_ids))

        return unique_job_ids


# Usage example:
if __name__ == "__main__":
    # The credentials will be loaded from the secrets.json file
    gmail = GmailRetriever()

    # Method 4: Get all messages from a specific sender
    sender_email = "emmanuel.pean@gmail.com"
    ids = gmail.search_messages("")
    print(ids)
    body1 = gmail.get_message_content(ids[0])["body"]
    print(gmail.extract_linkedin_job_ids(body1))
