from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .models import Users


class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate using either email or username"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:

            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that works with your Users model"""

    def get_user(self, validated_token):
        try:

            user_id = validated_token.get("user_id")
            if not user_id:
                raise AuthenticationFailed("No user_id in token", code="invalid_token")

            user = Users.objects.get(id=user_id, is_active=True)
            return user

        except Users.DoesNotExist:
            raise AuthenticationFailed("User not found", code="user_not_found")
