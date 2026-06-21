"""Stripe Customer API"""

import time

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from app.config import settings
from app.models import User
from app.payments import stripe, logger


async def create_customer(user: User) -> stripe.Customer:
    """Create a Stripe customer, with test clock if in test mode.
    :param user: User object
    :return: Customer object"""

    customer_params = {"email": user.email, "metadata": {"user_id": str(user.id)}}

    if settings.test_mode:
        test_clock = await stripe.test_helpers.TestClock.create_async(
            frozen_time=int(time.time()),
            name=f"Test clock for user {user.id}",
        )
        customer_params["test_clock"] = test_clock.id
        logger.info(f"Created test clock {test_clock.id} for user {user.id}")

    return await stripe.Customer.create_async(**customer_params)


async def get_or_create_stripe_customer(
    user: User,
    db: Session,
) -> str:
    """Get or create Stripe customer for the user.
    :param user: User object
    :param db: Database session
    :return: Customer ID string
    :raises HTTPException: On validation or Stripe errors"""

    try:
        # If the user as a customer id, retrieve the existing customer
        if user.stripe_details.customer_id:
            customer = await stripe.Customer.retrieve_async(user.stripe_details.customer_id)

            # If a non-deleted Stripe customer was found
            if customer and not getattr(customer, "deleted", False):  # noqa
                # Update Stripe email if it doesn't match our database
                if customer["email"] != user.email:
                    customer = await stripe.Customer.modify_async(user.stripe_details.customer_id, email=user.email)
                    logger.info(f"Updated Stripe customer {customer.id} email to {user.email}")
                else:
                    logger.info(f"Retrieved existing Stripe customer {customer.id} for user {user.id}")
            else:
                customer = await create_customer(user)
                user.stripe_details.customer_id = customer.id
                db.commit()
                logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        # If no customer, create one
        else:
            customer = await create_customer(user)
            user.stripe_details.customer_id = customer.id
            db.commit()
            logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        return user.stripe_details.customer_id

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service temporarily unavailable. Please try again.",
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred. Please try again.",
        )
