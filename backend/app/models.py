"""Central model import registry"""

from app.core.models import *  # noqa
from app.data_tables.models import *  # noqa
from app.job_email_scraping.models import *  # noqa
from app.job_rating.models import *  # noqa
from app.external_service_monitoring.stripe.models import *  # noqa
from app.external_service_monitoring.apify.models import *  # noqa
from app.external_service_monitoring.brightdata.models import *  # noqa
from app.external_service_monitoring.anthropic.models import *  # noqa
from app.external_service_monitoring.service.models import *  # noqa
