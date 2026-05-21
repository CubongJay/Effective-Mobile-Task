from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import Users


class CustomJWTAuthentication(JWTAuthentication):
    """JWT authentication for the custom Users model."""

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed("No user_id in token", code="invalid_token")

        try:
            return Users.objects.get(id=user_id, is_active=True)
        except Users.DoesNotExist:
            raise AuthenticationFailed("User not found", code="user_not_found")
