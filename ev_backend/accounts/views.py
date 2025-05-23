from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import CustomUser
from .utils import generate_otp, send_otp_email
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.timezone import now
import datetime
from django.utils import timezone
from datetime import timedelta


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            user.otp = otp
            user.last_otp_sent_at = timezone.now()



            # 🚨 Make user a superuser (if needed)
            if user.email == 'jalalpuraks@gmail.com':  # Optional condition
                user.is_superuser = True
                user.is_staff = True

            user.save()
            send_otp_email(user.email, otp)
            return Response({"msg": "User created. OTP sent to email.","otp":otp}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)

            if user.email_verified:
                return Response({"message": "Email is already verified."}, status=status.HTTP_200_OK)
            
            # ⏱ Enforce cooldown
            cooldown_period = timedelta(seconds=60)
            now = timezone.now()

            if user.last_otp_sent_at and now - user.last_otp_sent_at < cooldown_period:
                remaining = cooldown_period - (now - user.last_otp_sent_at)
                return Response(
                    {"error": f"Please wait {int(remaining.total_seconds())} seconds before resending OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Generate and send new OTP
            new_otp = generate_otp()
            user.otp = new_otp
            user.last_otp_sent_at = now
            user.save()
            send_otp_email(user.email, new_otp)

            return Response({"message": "OTP has been resent to your email."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(APIView):
    # allow any user to verify their email
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        try:
            user = CustomUser.objects.get(email=email)
            if user.otp == otp:
                user.email_verified = True
                user.otp = ''
                user.save()

                refresh = RefreshToken.for_user(user)

                return Response({
                    "msg": "Email verified, logged in.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid OTP"}, status=400)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get('refresh')
            if not refresh:
                return Response({'error': 'Refresh token not found.'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Auto-login: generate new tokens
        refresh = RefreshToken.for_user(instance)
        return Response({
            "msg": "Profile updated.",
            "access": str(refresh.access),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)

    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                "access": response.data.get("access"),
                "refresh": response.data.get("refresh")
            }, status=status.HTTP_200_OK)
        return response
    
class CustomTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh')

        if not refresh:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh)
            access = str(refresh.access_token)

            return Response({
                "access": access,
                # "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            otp = generate_otp()
            user.otp = otp
            user.last_otp_sent_at = timezone.now()
            user.save()
            send_otp_email(user.email, otp)
            return Response({"message": "OTP sent to your email for password reset."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)



class VerifyOTPForPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not all([email, otp]):
            return Response(
                {"error": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            if user.otp != otp:
                return Response(
                    {"error": "Invalid OTP."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate a short-lived token (e.g., 5-minute expiry)
            reset_token = RefreshToken.for_user(user).access_token
            reset_token.set_exp(lifetime=timedelta(minutes=5))

            return Response({
                "message": "OTP verified. Proceed to reset password.",
                "reset_token": str(reset_token)
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
class ResetPasswordWithTokenView(APIView):
    permission_classes = [IsAuthenticated]  # Token must be valid

    def post(self, request):
        new_password = request.data.get("new_password")
        verify_password = request.data.get("verify_password")

        if not all([new_password, verify_password]):
            return Response(
                {"error": "New password and confirmation are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != verify_password:
            return Response(
                {"error": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.set_password(new_password)
        user.otp = ""  # Clear OTP after successful reset
        user.save()

        return Response(
            {"message": "Password reset successful."},
            status=status.HTTP_200_OK
        )
# class ResetPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         otp = request.data.get("otp")
#         new_password = request.data.get("new_password")
#         verify_password = request.data.get("verify_password")
#         if new_password != verify_password:
#             return Response({"error": "New password and verify password do not match."}, status=status.HTTP_400_BAD_REQUEST)

#         if not all([email, otp, new_password]):
#             return Response({"error": "Email, OTP, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = CustomUser.objects.get(email=email)

#             if user.otp != otp:
#                 return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

#             user.set_password(new_password)
#             user.otp = ""
#             user.save()
#             return Response({"message": "Password reset successful. You can now log in."}, status=status.HTTP_200_OK)

#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class ResendPasswordResetOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            
            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Rate limiting
            cooldown_period = timedelta(seconds=60)
            now = timezone.now()

            if user.last_otp_sent_at and now - user.last_otp_sent_at < cooldown_period:
                remaining = cooldown_period - (now - user.last_otp_sent_at)
                return Response(
                    {"error": f"Wait {int(remaining.total_seconds())}s to resend OTP."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Optional: Max 5 per hour logic (incremental lockout)
            one_hour_ago = now - timedelta(hours=1)
            if user.otp_sent_count and user.last_otp_sent_at and user.last_otp_sent_at > one_hour_ago:
                if user.otp_sent_count >= 5:
                    return Response({"error": "Max OTP resend attempts reached. Try after some time."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                user.otp_sent_count += 1
            else:
                user.otp_sent_count = 1
                user.last_otp_sent_at = now

            otp = generate_otp()
            user.otp = otp
            user.last_otp_sent_at = now
            user.save()
            send_otp_email(user.email, otp)

            return Response({"message": "OTP sent for password reset."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)