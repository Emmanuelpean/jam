"""Script to set up Stripe products and prices."""

from app.payments import stripe


def setup_stripe_products() -> None:
    """Set up Stripe products and prices."""

    premium_product = stripe.Product.create(name="TOAST")
    premium_price = stripe.Price.create(
        product=premium_product.id, unit_amount=500, currency="GBP", recurring={"interval": "month"}
    )
    print(f"Created product {premium_product.id} with price {premium_price.id}")


if __name__ == "__main__":
    setup_stripe_products()
