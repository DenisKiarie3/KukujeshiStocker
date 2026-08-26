"""
Thin wrapper around Paystack's REST API. Isolated here so that services.py
and views.py never build raw HTTP calls themselves, and so this is the one
place to mock in tests. Paystack has no official Python SDK; raw requests
is the documented, recommended approach.
"""
import requests
from django.conf import settings


class PaystackError(Exception):
    """Raised when Paystack returns a non-success response or is unreachable."""


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(*, email, amount_kobo, reference, callback_url, currency="KES"):
    """
    Amount is in the currency's subunit (kobo/cents) — Paystack always
    works in the smallest unit, so KES 250.00 is passed as 25000.
    """
    payload = {
        "email": email,
        "amount": amount_kobo,
        "reference": reference,
        "callback_url": callback_url,
        "currency": currency,
    }
    try:
        response = requests.post(
            f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload, headers=_headers(), timeout=15,
        )
    except requests.RequestException as exc:
        raise PaystackError(f"Could not reach Paystack: {exc}") from exc

    data = response.json()
    if not data.get("status"):
        raise PaystackError(data.get("message", "Paystack initialization failed."))
    return data["data"]  # { authorization_url, access_code, reference }


def verify_transaction(*, reference):
    try:
        response = requests.get(
            f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=_headers(), timeout=15,
        )
    except requests.RequestException as exc:
        raise PaystackError(f"Could not reach Paystack: {exc}") from exc

    data = response.json()
    if not data.get("status"):
        raise PaystackError(data.get("message", "Paystack verification failed."))
    return data["data"]  # { status, amount, currency, reference, ... }