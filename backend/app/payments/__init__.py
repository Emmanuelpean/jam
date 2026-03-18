"""Payment-related API routes using Stripe for subscription management."""

import stripe
from fastapi import APIRouter

from app.config import settings
from app.utils import AppLogger

stripe.api_key = settings.stripe_api_key
logger = AppLogger.get_logger("Stripe")
