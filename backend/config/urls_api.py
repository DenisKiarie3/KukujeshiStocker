from django.urls import path, include

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.inventory.urls")),
    path("", include("apps.orders.urls")),
    path("", include("apps.payments.urls")),
]