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
}


TEST_EMAILS = [
    INDEED_EMAIL_1,
    INDEED_EMAIL_2,
    LINKEDIN_EMAIL_1,
    LINKEDIN_EMAIL_2,
    VEGANJOBS_EMAIL_1,
]
TEST_EMAILS = {email["id"]: email for email in TEST_EMAILS}
