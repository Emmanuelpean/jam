"""
Central model import registry.

Importing this module guarantees that all SQLAlchemy models
are registered on Base.metadata before first use.
"""

# noinspection PyUnusedImports
from app.models import *

# noinspection PyUnusedImports
from app.job_rating.models import *

# noinspection PyUnusedImports
from app.eis.models import *
