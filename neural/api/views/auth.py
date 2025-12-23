"""Authentication views for API v1."""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.api.serializers.auth import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class LoginView(APIView):
    """Login view - returns auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    """Register view - creates new user."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Usuario creado exitosamente",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "is_verified": user.is_verified,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """View for getting and updating current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Logout view - deletes auth token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's token
        Token.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Sesión cerrada exitosamente"},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    """Request password reset email."""

    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.forms import PasswordResetForm

        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = PasswordResetForm(data={"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
            )

        # Always return success to prevent email enumeration
        return Response(
            {"message": "Se ha enviado un correo con instrucciones"},
            status=status.HTTP_200_OK,
        )
