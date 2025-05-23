from django.urls import path
from .views import (
    RegisterView, CustomTokenObtainPairView, UserDetailView,
    PasswordResetRequestView, PasswordResetConfirmView, ManualLogoutView, CustomTokenRefreshView
)
from drf_yasg.utils import swagger_auto_schema

# We'll use standard URL patterns without the complex decorators
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", ManualLogoutView.as_view(), name="logout"),
    # Forgot Password URLs
    path("forgot-password/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("reset-password/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
