"""Router to get email templates"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from app import models
from app.config import settings
from app.core import oauth2
from app.emails.templates import email_templates
from app.routers.utility import assert_admin

email_template_router = APIRouter(prefix="/email-templates", tags=["email-templates"])


class EmailTemplatePreview(BaseModel):
    """A previewable email template: its id, human-readable label, and rendered HTML."""

    id: str
    label: str
    html: str


# Human-readable labels for each template, shown in the preview UI. Keys must match _SAMPLE_DATA.
_TEMPLATE_LABELS: dict[str, str] = {
    "email_confirmation": "Email Confirmation",
    "password_reset": "Password Reset",
    "email_change": "Email Change Verification",
    "password_changed": "Password Changed",
    "email_changed": "Email Changed",
    "trial_end_reminder": "Trial End Reminder",
    "new_version": "New Version Announcement",
}

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


def _render_template(template_name: str) -> str:
    """Render a single email template with its sample data.
    :param template_name: The template name (without .html extension).
    :returns: Rendered HTML content of the email template.
    :raises HTTPException: 404 if the template is unknown, 500 if Jinja2 is not initialised."""

    if template_name not in _SAMPLE_DATA:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template '{template_name}' not found")

    if not email_templates.env:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Jinja2 environment not initialised"
        )

    template = email_templates.env.get_template(f"{template_name}.html")
    return template.render(**_SAMPLE_DATA[template_name])


@email_template_router.get("/", response_model=list[EmailTemplatePreview])
def preview_all_email_templates(
    current_user: models.User = Depends(oauth2.get_current_user),
) -> list[EmailTemplatePreview]:
    """Render every email template with sample data. Admin only.
    :param current_user: The current authenticated admin user.
    :returns: List of templates, each with its id, label, and rendered HTML content."""

    assert_admin(current_user)

    return [
        EmailTemplatePreview(id=name, label=_TEMPLATE_LABELS[name], html=_render_template(name))
        for name in _SAMPLE_DATA
    ]
