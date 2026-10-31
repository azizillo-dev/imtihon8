from django.urls import path

from .views import (
    LoginView,
    PasswordChangeView,
    ProfileUpdateView,
    ProfileView,
    RegisterView,
    ResendCodeView,
    VerifyEmailView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("resend-code/", ResendCodeView.as_view(), name="resend-code"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile-update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("change-password/", PasswordChangeView.as_view(), name="change-password"),
]
