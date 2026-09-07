from django.urls import path

from .views import (
    StorefrontProductListView,
    StorefrontOrderCreateView,
    StorefrontOrderStatusView,
    StorefrontCheckoutView,
)

urlpatterns = [
    path("storefront/<slug:slug>/products/", StorefrontProductListView.as_view(), name="storefront-products"),
    path("storefront/<slug:slug>/orders/", StorefrontOrderCreateView.as_view(), name="storefront-order-create"),
    path("storefront/orders/<uuid:public_reference>/checkout/", StorefrontCheckoutView.as_view(), name="storefront-checkout"),
    path("storefront/orders/<uuid:public_reference>/status/", StorefrontOrderStatusView.as_view(), name="storefront-order-status"),
]