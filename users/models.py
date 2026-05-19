from django.db import models
from .constants import UserRole


class Users(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=50, choices=UserRole.choices(), default=UserRole.USER.value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_authenticated(self):
        """Required for DRF's IsAuthenticated permission"""
        return True

    @property
    def is_anonymous(self):
        """Required for DRF"""
        return False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
