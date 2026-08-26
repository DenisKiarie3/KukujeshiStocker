import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import confirm_paystack_payment


def _signature_is_valid(request):
    """
    HMAC SHA512 of the RAW request body, keyed with the Paystack secret,
    compared in constant time against the x-paystack-signature header.
    Must use request.body (raw bytes) — re-serializing request.data would
    change byte-for-byte content and never match.
    """
    signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
    if not signature or not settings.PAYSTACK_SECRET_KEY:
        return False
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        request.body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    # Signature check FIRST — before parsing, before any DB work. An
    # unsigned or wrongly-signed request never touches the payment logic.
    if not _signature_is_valid(request):
        return HttpResponseForbidden("Invalid signature.")

    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if event.get("event") == "charge.success":
        reference = event.get("data", {}).get("reference")
        if reference:
            confirm_paystack_payment(reference=reference)

    # Always 200 for any validly-signed event, even ones we don't act on —
    # otherwise Paystack retries deliveries it shouldn't need to.
    return HttpResponse(status=200)