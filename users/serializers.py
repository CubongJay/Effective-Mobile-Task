from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Users
import bcrypt


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "is_active",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):

        password = data.get("password")

        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                "The password and verify password must match"
            )

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data["password"]
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        validated_data["password"] = hashed_password.decode("utf-8")

        return super().create(validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that uses email instead of username"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"] = serializers.EmailField()

        self.fields.pop("username", None)

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = Users.objects.get(email=email, is_active=True)
        except Users.DoesNotExist:
            raise serializers.ValidationError(
                "No active account found with the given credentials"
            )

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            raise serializers.ValidationError(
                "No active account found with the given credentials"
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
