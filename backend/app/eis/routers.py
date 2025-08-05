from app.eis.models import JobAlertEmail
from app.eis.schemas import (
    Email,
    EmailUpdate,
    EmailOut,
    ScrapedJob,
    ScrapedJobUpdate,
    ScrapedJobOut,
    ServiceLog,
    ServiceLogUpdate,
    ServiceLogOut,
)
from app.routers.tables import generate_crud_router

email_router = generate_crud_router(
    table_model=JobAlertEmail,
    create_schema=Email,
    update_schema=EmailUpdate,
    out_schema=EmailOut,
    endpoint="jobalertemails",
    not_found_msg="Job alert email not found",
)


scrapedjob_router = generate_crud_router(
    table_model=ScrapedJob,
    create_schema=ScrapedJob,
    update_schema=ScrapedJobUpdate,
    out_schema=ScrapedJobOut,
    endpoint="scrapedjobs",
    not_found_msg="Scraped job not found",
)

servicelog_router = generate_crud_router(
    table_model=ServiceLog,
    create_schema=ServiceLog,
    update_schema=ServiceLogUpdate,
    out_schema=ServiceLogOut,
    endpoint="servicelogs",
    not_found_msg="Service log not found",
    admin_only=True,
)
