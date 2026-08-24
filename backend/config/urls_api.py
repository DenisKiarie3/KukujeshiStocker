from django.urls import path, include

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.inventory.urls")),
]