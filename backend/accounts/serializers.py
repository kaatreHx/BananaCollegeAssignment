"""Serializers for the identity API."""

import uuid

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Player


def tokens_for(player: Player) -> dict:
    refresh = RefreshToken.for_user(player)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "name", "email", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """email + name + password  →  a new Player."""

    name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name is required.")
        return value

    def validate_email(self, value):
        if Player.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with that email already exists.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return Player.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=validated_data["password"],
        )


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login by email + password. Also returns the player."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["name"] = user.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["player"] = PlayerSerializer(self.user).data
        return data
