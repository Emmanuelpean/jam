"""Email parsers package for processing job-related emails."""

from app.job_email_scraping.email_parsers import indeed, linkedin, nhs, veganjobs
from app.job_email_scraping.email_parsers.utils import Platform

JOB_PARSERS = {
    Platform.LINKEDIN: linkedin.parse_linkedin_job_email,
    Platform.INDEED: indeed.parse_indeed_job_email,
    Platform.VEGANJOBS: veganjobs.parse_veganjobs_email,
    Platform.NHS: nhs.parse_nhs_job_email,
}

ALERT_NAME_EXTRACTORS = {
    Platform.LINKEDIN: lambda subject, body: linkedin.extract_alert_name(subject),
    Platform.INDEED: lambda subject, body: indeed.extract_alert_name(subject),
    Platform.VEGANJOBS: lambda subject, body: veganjobs.extract_alert_name(subject),
    Platform.NHS: lambda subject, body: nhs.extract_alert_name(body),
}

PLATFORM_SENDER_EMAILS = {
    "jobalerts-noreply@linkedin.com": Platform.LINKEDIN,
    "alert@indeed.com": Platform.INDEED,
    "nhs.jobs.job.alerts@notifications.service.gov.uk": Platform.NHS,
    "info@veganjobs.com": Platform.VEGANJOBS,
}
