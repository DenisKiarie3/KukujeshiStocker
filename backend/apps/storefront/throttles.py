from rest_framework.throttling import AnonRateThrottle


class StorefrontReadThrottle(AnonRateThrottle):
    """Generous limit for browsing the public catalog."""
    scope = "storefront_read"


class StorefrontOrderThrottle(AnonRateThrottle):
    """Tighter limit on anonymous order creation — the abuse-sensitive path."""
    scope = "storefront_order"