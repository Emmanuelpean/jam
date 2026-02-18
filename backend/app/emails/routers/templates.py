"""Router to get email templates"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from app import models
from app.config import settings
from app.core import oauth2
from app.routers import assert_admin

router = APIRouter(prefix="/email-templates", tags=["email-templates"])

_templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

_SAMPLE_DATA: dict[str, dict] = {
    "email_confirmation": {
        "name": "Jane Smith",
        "confirmation_url": "https://example.com/verify-email/?token=abc123xyz",
        "token_expiry_min": settings.verification_token_expiration_minutes,
    },
    "password_reset": {
        "name": "Jane Smith",
        "reset_url": "https://example.com/reset-password/?token=abc123xyz",
        "token_expiry_min": settings.password_reset_token_expiration_minutes,
    },
    "email_change": {
        "name": "Jane Smith",
        "confirmation_url": "https://example.com/verify-new-email/?token=abc123xyz",
        "token_expiry_min": settings.email_change_token_expiration_minutes,
    },
    "password_changed": {
        "change_date": "February 18, 2026 at 02:30 PM UTC",
        "support_email": settings.support_email,
    },
    "email_changed": {
        "change_date": "February 18, 2026 at 02:30 PM UTC",
        "support_email": settings.support_email,
        "old_email": "jane.old@example.com",
        "new_email": "jane.new@example.com",
    },
    "trial_end_reminder": {
        "upgrade_url": settings.frontend_url + "/settings/premium",
        "end_date": "March 1, 2026",
        "support_email": settings.support_email,
    },
    "new_version": {
        "version": settings.app_version,
        "features": [
            {
                "title": "Email Template Previewer",
                "description": "Admins can now preview all email templates directly in the app.",
            },
            {
                "title": "Improved Job Alerts",
                "description": "Job alerts now support more filtering options for better matches.",
            },
            {
                "title": "Dark Mode Enhancements",
                "description": "Refined colour palette for better readability in dark mode.",
            },
        ],
        "app_url": settings.frontend_url,
    },
}


@router.get("/preview/{template_name}", response_class=HTMLResponse)
def preview_email_template(
    template_name: str,
    current_user: models.User = Depends(oauth2.get_current_user),
) -> str:
    """Render an email template with sample data and return it as HTML. Admin only.
    :param template_name: The template name (without .html extension).
    :param current_user: The current authenticated admin user.
    :returns: Rendered HTML content of the email template."""

    assert_admin(current_user)

    if template_name not in _SAMPLE_DATA:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template '{template_name}' not found")

    template = _templates.env.get_template(f"{template_name}.html")
    return template.render(**_SAMPLE_DATA[template_name])
