from django.urls import path

from .views import StorefrontProductListView

urlpatterns = [
    path("storefront/<slug:slug>/products/", StorefrontProductListView.as_view(), name="storefront-products"),
]