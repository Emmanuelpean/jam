"""Release slide data for version announcement emails.

Python equivalent of frontend releaseSlides from versions.ts.
"""

PREMIUM_PRICE = "£7"

RELEASE_SLIDES: dict[str, list[dict]] = {
    "1.0.0": [
        {
            "title": "Job Application Tracking",
            "description": "Create and manage detailed job application records from a centralised dashboard.",
        },
        {
            "title": "Interview Scheduling",
            "description": "Log interview dates, times, and types. Keep a clear timeline of your stages.",
        },
        {
            "title": "Company & Contact Management",
            "description": "Store company details and link contacts, emails, and LinkedIn profiles to applications.",
        },
        {
            "title": "Application Status Monitoring",
            "description": "Track applications through customisable statuses and monitor deadlines at a glance.",
        },
        {
            "title": "Email Verification & Password Reset",
            "description": "Secure your account with email verification and easy password resets.",
        },
    ],
    "1.1.0": [
        {
            "title": "Job Scraping & Rating (Alpha)",
            "description": "JAM Premium extracts job alert data from your emails and rates each job using AI.",
        },
        {
            "title": "AI Job Rating",
            "description": "Scraped jobs are automatically rated based on your qualifications.",
        },
        {
            "title": "UI Improvements",
            "description": "Better theme contrast, sorted select options, and company names in selects.",
        },
        {
            "title": "Bug Fixes",
            "description": "Fixed source aggregator display, modal refresh, and theme name updates.",
        },
    ],
    "1.2.0": [
        {
            "title": "Job Alert Filters",
            "description": "Create rules to exclude unwanted jobs by company, title, or other parameters.",
        },
        {
            "title": "Speculative Applications",
            "description": "A dedicated page for tracking speculative and spontaneous applications.",
        },
        {
            "title": "Follow-Up Email Generator",
            "description": "Right-click a job to generate a personalised follow-up email to its contacts.",
        },
        {
            "title": "JAM Premium",
            "description": f"For only {PREMIUM_PRICE}/month, JAM automatically scrapes job alert emails details, "
            "rates them against your qualifications, and highlights the best matches for you. "
            "New users get a 14-day free trial.",
        },
        {
            "title": "Dark Mode & UI Refresh",
            "description": "Dark mode, reworked settings page, editable badges, and account deletion.",
        },
        {
            "title": "Quality of Life Improvements",
            "description": "Extended data export, new job source types, and improved error messages.",
        },
    ],
    "1.3.0": [
        {
            "title": "Customisable Dashboard",
            "description": "Your dashboard is now fully customisable. Add, remove, resize, and rearrange widgets in "
            "edit mode. Choose from Metric, Table, Timeline, Graph, and Map widget types, or build a "
            "custom graph from your own data.",
        },
        {
            "title": "Customisable Table Columns",
            "description": "All data tables now support column customisation. Show or hide columns to focus on what "
            "matters, with preferences saved per table.",
        },
        {
            "title": "Favourite Filters for Job Alerts",
            "description": "Use filters to highlights matching jobs at a glance.",
        },
        {
            "title": "CV & Cover Letter Attachments",
            "description": "Attach a CV and cover letter directly to a job application.",
        },
    ],
}


def get_release_slides(version: str) -> list[dict] | None:
    """Get the release slides for a given version.
    :param version: The version string (e.g. "1.2.0")
    :returns: List of feature dicts, or None if version not found."""

    return RELEASE_SLIDES.get(version)
