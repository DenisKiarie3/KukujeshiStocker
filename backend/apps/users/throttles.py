from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Applied only to auth endpoints (register/login) — per the project's
    security requirements, throttling belongs on auth endpoints at
    minimum, since they're the natural target for brute-force attempts.
    """
    scope = "auth"