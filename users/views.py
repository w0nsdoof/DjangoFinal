import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import AccessLog
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from .serializers import (
    UserRegistrationSerializer, CustomTokenObtainPairSerializer,
    UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()
logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Helper function to get the client's IP address from the request.
    
    Checks for X-Forwarded-For header first, then falls back to REMOTE_ADDR.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client's IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint that allows users to obtain JWT tokens.
    
    This view generates a pair of tokens (access and refresh) upon successful authentication.
    It also logs login attempts and tracks user IP addresses.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Authenticates a user and returns JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            200: openapi.Response(
                description="Authentication successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Authentication failed"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Authenticate a user and return JWT tokens.
        
        Parameters:
            email: User's email
            password: User's password
            
        Returns:
            200: JWT tokens (access and refresh)
            401: Authentication failed
        """
        email = request.data.get("email", "")
        ip = get_client_ip(request)

        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                user = User.objects.get(email=email)

                # IP-логика
                if user.last_login_ip != ip:
                    logger.warning(f"🕵️ New login IP detected: {ip} for {email}")
                user.last_login_ip = ip

                # Сброс безопасный, но не обязателен — уже делается в validate()
                user.save()

                logger.info(f"✅ JWT Login: {email} (IP: {ip})")
                AccessLog.objects.create(
                    user=user,
                    action="login",
                    ip_address=ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

            return response

        except AuthenticationFailed as e:
            logger.warning(f"❌ Failed login: {email} (IP: {ip}) — {str(e)}")
            raise


class CustomTokenRefreshView(TokenRefreshView):
    """
    API endpoint that allows users to refresh their JWT access token.
    
    This view takes a refresh token and returns a new access token.
    It logs token refresh attempts with IP address information.
    """
    
    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description="Use a refresh token to obtain a new access token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description="Token refresh successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Invalid refresh token"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Refresh an access token using a refresh token.
        
        Parameters:
            refresh: Refresh token
            
        Returns:
            200: New access token
            401: Invalid refresh token
        """
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            logger.info(f"Обновление токена (IP: {get_client_ip(request)})")

        return response


class ManualLogoutView(APIView):
    """
    API endpoint for user logout functionality.
    
    This view logs the logout action and creates an entry in the AccessLog.
    Authentication is required.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="User logout",
        operation_description="Logs user logout event",
        responses={
            200: openapi.Response(
                description="Logout successfully logged",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        """
        Log a user's logout action.
        
        Authentication required via JWT token.
        
        Returns:
            200: Logout successfully logged
        """
        user = request.user
        ip = get_client_ip(request)
        logger.info(f"JWT-выход: {user.email} (IP: {ip})")
        AccessLog.objects.create(
            user=user,
            action='logout',
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return Response({"message": "Logout logged"})


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    This view creates a new user account. No authentication is required.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register new user",
        operation_description="Creates a new user account",
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Registration failed with error details"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Register a new user account.
        
        Parameters are defined in the UserRegistrationSerializer.
        
        Returns:
            201: User registered successfully with role
            400: Registration failed with error message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                user = serializer.save()
                logger.info(f"Успешная регистрация: {user.email}")
                return Response({"message": "User registered successfully.", "role": user.role},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Ошибка регистрации пользователя: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user details.
    
    This view returns the current authenticated user's profile information.
    Authentication is required.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get current user details",
        operation_description="Returns the profile of the currently authenticated user",
        responses={
            200: UserSerializer,
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """
        Get the current authenticated user's profile.
        
        Returns:
            200: User profile data
            401: Authentication credentials were not provided
        """
        return super().get(request, *args, **kwargs)

    def get_object(self):
        """
        Get the current authenticated user object.
        
        Returns:
            User: The current authenticated user
        """
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    """
    API endpoint for requesting a password reset.
    
    This view sends a password reset email to the user's registered email address.
    No authentication is required.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Request password reset",
        operation_description="Sends a password reset email to the user's email address",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    format=openapi.FORMAT_EMAIL,
                    description="User's registered email address"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Password reset email sent (if email exists)",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "User with this email does not exist",
            500: "Failed to send email"
        }
    )
    def post(self, request):
        """
        Request a password reset email.
        
        Parameters:
            email: User's registered email address
            
        Returns:
            200: If email is registered, a password reset link will be sent
            400: User with this email does not exist
            500: Failed to send email
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            logger.warning(f"Запрос сброса пароля: email не найден — {email}")
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        try:
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Отправлен email сброса пароля пользователю: {user.email}")
            return Response({"message": "If your email is registered, you will receive a password reset link."})
        except Exception as e:
            logger.error("Ошибка при отправке письма для сброса пароля: %s", e)
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    API endpoint for confirming a password reset.
    
    This view validates the reset token and sets a new password for the user.
    No authentication is required.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Confirm password reset",
        operation_description="Validates token and sets new password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_password'],
            properties={
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="New password to set"
                ),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                'uidb64',
                openapi.IN_PATH,
                description="URL-safe base64 encoded user ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'token',
                openapi.IN_PATH,
                description="Password reset token",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Password reset successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Invalid token or user not found"
        }
    )
    def put(self, request, uidb64, token):
        """
        Confirm a password reset and set a new password.
        
        Parameters:
            uidb64: URL-safe base64 encoded user ID
            token: Password reset token
            new_password: New password from request body
            
        Returns:
            200: Password has been reset successfully
            400: Invalid token or user not found
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                logger.warning("Невалидный токен сброса пароля для UID: %s", uid)
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            logger.info(f"Пароль сброшен пользователем: {user.email} (IP: {get_client_ip(request)})")
            return Response({"message": "Password has been reset successfully."})
        except Exception as e:
            logger.error("Ошибка подтверждения сброса пароля: %s", e)
            return Response({"error": "Invalid token or user not found"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileCompletionCheckView(generics.RetrieveAPIView):
    """
    API endpoint to check if a user's profile is complete.
    
    This view returns a boolean indicating whether the authenticated user's profile is completed.
    Authentication is required.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Check profile completion status",
        operation_description="Returns whether the user's profile is completed",
        responses={
            200: openapi.Response(
                description="Profile completion status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_profile_completed': openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="Whether the user's profile is completed"
                        )
                    }
                )
            ),
            401: "Authentication credentials were not provided"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """
        Check if the authenticated user's profile is complete.
        
        Returns:
            200: JSON with is_profile_completed boolean
        """
        return Response({"is_profile_completed": request.user.is_profile_completed})
