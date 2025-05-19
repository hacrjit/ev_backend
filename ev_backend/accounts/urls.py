from django.urls import path
from .views import RegisterView, ResendOTPView, VerifyOTPView, LogoutView, UserUpdateView, CustomTokenObtainPairView, CustomTokenRefreshView, ForgotPasswordView, ResendPasswordResetOTPView, VerifyOTPForPasswordResetView, ResetPasswordWithTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('verify-otp/', VerifyOTPView.as_view()),

    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_login'),              # for cookie based auth
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('logout/', LogoutView.as_view()),
    path('update/', UserUpdateView.as_view()),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp-for-password-reset/', VerifyOTPForPasswordResetView.as_view(), name='verify-otp-for-password-reset'),
    path('reset-password-with-token/', ResetPasswordWithTokenView.as_view(), name='reset-password-with-token'),
    # path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('resend-password-reset-otp/', ResendPasswordResetOTPView.as_view(), name='resend-password-reset-otp')

]
