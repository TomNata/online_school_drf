import stripe
from django.conf import settings


def create_stripe_payment(product_name):
    stripe.api_key = settings.STRIPE_TEST_API_KEY

    price = stripe.Price.create(
        currency="rub",
        unit_amount=100000,
        recurring={"interval": "month"},
        product_data={"name": product_name},
    )

    session = stripe.checkout.Session.create(
        success_url="https://example.com/success",
        line_items=[{"price": price['id'], "quantity": 1}],
        mode="subscription",
    )

    return session
