from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet
from .webhooks import paystack_webhook

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls + [
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),
]