"""This module contains test email resources for job alert emails from different platforms."""

import datetime
import os

from tests.utils.table_data import USER_DATA


def open_file(file: str) -> str:
    """Open a file and return its content
    :param file: The file to open
    :return: The contents of the file"""

    BASE_DIR = os.path.dirname(__file__)
    filepath = os.path.join(BASE_DIR, "../resources/job_alert_emails", file)
    with open(filepath, "r", encoding="utf8") as ofile:
        return ofile.read()


# ------------------------------------------------------ LINKEDIN ------------------------------------------------------

# Email 1
LINKEDIN_EMAIL_1_BODY = open_file("linkedin_email_1.txt")
LINKEDIN_JOB_IDS_1 = [
    "4289870503",
    "4291891707",
    "4291383265",
    "4280354992",
    "4255584864",
    "4265877117",
]
LINKEDIN_EMAIL_1 = {
    "id": "1",
    "subject": "Your job alert for embedded python in United Kingdom",
    "from": "jobalerts-noreply@linkedin.com",
    "to": USER_DATA[0]["email"],
    "date": datetime.datetime.now(),
    "body": LINKEDIN_EMAIL_1_BODY,
    "platform": "linkedin",
    "job_ids": LINKEDIN_JOB_IDS_1,
}

# Email 2
LINKEDIN_EMAIL_2_BODY = open_file("linkedin_email_2.txt")
LINKEDIN_JOB_IDS_2 = [
    "4313354836",
    "4303488973",
    "4218756028",
    "4306284473" "4255739214" "4313361714",
]
LINKEDIN_EMAIL_2 = {
    "id": "2",
    "subject": "Your job alert for embedded python in United Kingdom",
    "from": "jobalerts-noreply@linkedin.com",
    "to": USER_DATA[1]["email"],
    "date": datetime.datetime.now(),
    "body": LINKEDIN_EMAIL_2_BODY,
    "platform": "linkedin",
    "job_ids": LINKEDIN_JOB_IDS_2,
}


# ------------------------------------------------------- INDEED -------------------------------------------------------

# Email 1
INDEED_EMAIL_1_BODY = open_file("indeed_email_1.txt")
INDEED_JOB_IDS_1 = [
    "8799a57d87058103",
    "d489097ca0fb185f",
    "7f9c701ebf265b69",
    "0537336f99ba1650",
    "312725e138947a4b",
    "06498cad9de95b12",
    "bd60005166216639",
    "42b107e214095d56",
    "d30493c008b601e3",
    "da413431a0c55ec7",
    "2ed37852402643ab",
    "14a9001ba6ebb965",
    "eafb032fabcd77bc",
    "6838e604ddffd5ac",
    "227d4ccd0823fc96",
    "804b940d2d96b30b",
    "f9aafc9ba4c31c6d",
    "e034f0b761e410ea",
    "37cdb0ba59e12295",
    "7b272f46e4e46a14",
    "d6110bfb54bdeddb",
    "5aa22054e7a8b76e",
    "ae47862d410bbd39",
]
INDEED_EMAIL_1 = {
    "id": "3",
    "subject": "23 new R&D Development Engineer jobs",
    "from": "alert@indeed.com",
    "to": USER_DATA[0]["email"],
    "date": datetime.datetime.now(),
    "body": INDEED_EMAIL_1_BODY,
    "platform": "indeed",
    "job_ids": INDEED_JOB_IDS_1,
}

# Email 2
INDEED_EMAIL_2_BODY = open_file("indeed_email_2.txt")
INDEED_JOB_IDS_2 = [
    "77fb4f3c42ebc7c2",
    "ae868ef5ecdefc01",
    "6c6f8fffaffa1993",
]
INDEED_EMAIL_2 = {
    "id": "4",
    "subject": "New jobs at Snap Inc.",
    "from": "alert@indeed.com",
    "to": USER_DATA[1]["email"],
    "date": datetime.datetime.now(),
    "body": INDEED_EMAIL_2_BODY,
    "platform": "indeed",
    "job_ids": INDEED_JOB_IDS_2,
}

# ------------------------------------------------------ VEGANJOBS -----------------------------------------------------

# Email 1
VEGANJOBS_EMAIL_1_BODY = open_file("veganjobs_email_1.txt")
VEGANJOBS_JOB_IDS_1 = [
    "physicians-committee-for-responsible-medicine-remote-from-anywhere-in-the-united-states-building-healthy-communities-internship",
    "chill-gelato-canada-water-london-gelato-scooper",
]
VEGANJOBS_EMAIL_1 = {
    "id": "5",
    "subject": "We have found new job posts that match your job alert",
    "from": "info@veganjobs.com",
    "to": USER_DATA[0]["email"],
    "date": datetime.datetime.now(),
    "body": VEGANJOBS_EMAIL_1_BODY,
    "platform": "veganjobs",
    "job_ids": VEGANJOBS_JOB_IDS_1,
}

# --------------------------------------------------------- NHS --------------------------------------------------------

# Email 1
NHS_EMAIL_1_BODY = open_file("nhs_email_1.txt")
NHS_JOB_IDS_1 = [
    "C9342-25-1080",
    "H9110-25-1767",
    "H9040-25-1678",
    "H9110-25-1768",
    "H9110-25-1773",
    "M9043-25-0282",
]
NHS_EMAIL_1 = {
    "id": "6",
    "subject": "NHS job alerts for X",
    "from": "nhs.jobs.job.alerts@notifications.service.gov.uk",
    "to": USER_DATA[0]["email"],
    "date": datetime.datetime.now(),
    "body": NHS_EMAIL_1_BODY,
    "platform": "nhs",
    "job_ids": NHS_JOB_IDS_1,
}

# Email 2
NHS_EMAIL_2_BODY = open_file("nhs_email_2.txt")
NHS_JOB_IDS_2 = [
    "H9110-25-1765",
    "H9001-25-0803",
    "M9043-25-0287",
    "C9028-25-0356",
    "H9001-25-0804",
    "C9342-25-1098",
    "M9043-25-0284",
    "H9110-25-1772",
    "C8120-25-0101",
    "H9110-25-1777",
]
NHS_EMAIL_2 = {
    "id": "7",
    "subject": "NHS job alerts for X",
    "from": "nhs.jobs.job.alerts@notifications.service.gov.uk",
    "to": USER_DATA[0]["email"],
    "date": datetime.datetime.now(),
    "body": NHS_EMAIL_2_BODY,
    "platform": "nhs",
    "job_ids": NHS_JOB_IDS_2,
}

TEST_EMAILS = [
    LINKEDIN_EMAIL_1,
    LINKEDIN_EMAIL_2,
    INDEED_EMAIL_1,
    INDEED_EMAIL_2,
    VEGANJOBS_EMAIL_1,
    NHS_EMAIL_1,
    NHS_EMAIL_2,
]
NEW_TEST_EMAILS = {}
for user in USER_DATA:
    for email in TEST_EMAILS:
        email = email.copy()
        email["to"] = user["email"]
        email["id"] = f"{email['id']}_{user['email']}"
        NEW_TEST_EMAILS[email["id"]] = email
TEST_EMAILS = NEW_TEST_EMAILS
