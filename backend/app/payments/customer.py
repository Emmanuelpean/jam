"""Stripe Customer API"""

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import User
from app.payments import stripe, logger


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
            if customer and not customer.get("deleted", False):
                # Update Stripe email if it doesn't match our database
                if customer.email != user.email:
                    customer = await stripe.Customer.modify_async(user.stripe_details.customer_id, email=user.email)
                    logger.info(f"Updated Stripe customer {customer.id} email to {user.email}")
                else:
                    logger.info(f"Retrieved existing Stripe customer {customer.id} for user {user.id}")
            else:
                customer = await stripe.Customer.create_async(email=user.email, metadata={"user_id": str(user.id)})
                user.stripe_details.customer_id = customer.id
                db.commit()
                logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        # If no customer, create one
        else:
            customer = await stripe.Customer.create_async(email=user.email, metadata={"user_id": str(user.id)})
            user.stripe_details.customer_id = customer.id
            db.commit()
            logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")

        return user.stripe_details.customer_id

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable. Please try again.")
    except SQLAlchemyError as e:
        logger.error(f"Database error for user {user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")
