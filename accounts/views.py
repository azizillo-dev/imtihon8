from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    ResendCodeSerializer,
    VerifyEmailSerializer,
)
from .services import create_and_send_verification_code, verify_code


def token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Tasdiqlash kodi emailingizga yuborildi."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyEmailSerializer)
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        if not verify_code(email, code):
            return Response(
                {"detail": "Tasdiqlash kodi noto'g'ri yoki muddati o'tgan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.filter(email=email).first()
        if user:
            user.is_active = True
            user.save(update_fields=["is_active"])
            return Response(
                {"detail": "Email tasdiqlandi."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Foydalanuvchi topilmadi."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = get_user_model().objects.filter(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                return Response(
                    {"detail": "Email tasdiqlanmagan."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "Kirish muvaffaqiyatli.", "tokens": token_response(user)},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Email yoki parol noto'g'ri."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendCodeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ResendCodeSerializer)
    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = get_user_model().objects.filter(email=email, is_active=False).first()
        if not user:
            return Response(
                {"detail": "Foydalanuvchi topilmadi yoki email allaqachon tasdiqlangan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_and_send_verification_code(user.email)
        return Response(
            {"detail": "Yangi tasdiqlash kodi emailingizga yuborildi."},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ProfileUpdateSerializer)
    def patch(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"detail": "Eski parol noto'g'ri."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Parol muvaffaqiyatli o'zgartirildi."},
            status=status.HTTP_200_OK,
        )




