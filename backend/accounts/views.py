"""Identity HTTP API: register, login, me."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, PlayerSerializer, RegisterSerializer, tokens_for


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.save()
        return Response(
            {"player": PlayerSerializer(player).data, "tokens": tokens_for(player)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST {email, password} → {access, refresh, player}."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"player": PlayerSerializer(request.user).data})
