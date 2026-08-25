from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer
from .throttles import AuthRateThrottle

User = get_user_model()


def _set_refresh_cookie(response, refresh_token):
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=str(refresh_token),
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/api/v1/auth/",  # scoped narrowly — not sent on ordinary API calls, only auth ones
        max_age=max_age,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data, "access": str(refresh.access_token)},
            status=status.HTTP_201_CREATED,
        )
        _set_refresh_cookie(response, refresh)
        get_token(request)  # flags the csrftoken cookie to be issued alongside it
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        user = authenticate(
            request, username=request.data.get("username"), password=request.data.get("password")
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data, "access": str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )
        _set_refresh_cookie(response, refresh)
        get_token(request)
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not raw_token:
            return Response({"detail": "No refresh token cookie present."}, status=status.HTTP_401_UNAUTHORIZED)

        csrf_cookie = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
        csrf_header = request.META.get("HTTP_X_CSRFTOKEN")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return Response({"detail": "CSRF check failed."}, status=status.HTTP_403_FORBIDDEN)

        try:
            old_refresh = RefreshToken(raw_token)
        except TokenError:
            return Response({"detail": "Refresh token invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(pk=old_refresh["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User no longer exists."}, status=status.HTTP_401_UNAUTHORIZED)

        old_refresh.blacklist()
        new_refresh = RefreshToken.for_user(user)

        response = Response(
            {"access": str(new_refresh.access_token), "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        _set_refresh_cookie(response, new_refresh)
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if raw_token:
            try:
                RefreshToken(raw_token).blacklist()
            except TokenError:
                pass  # already invalid/expired — nothing more to do
        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie(settings.AUTH_COOKIE_NAME, path="/api/v1/auth/")
        return response