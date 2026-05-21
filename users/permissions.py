from rest_framework.permissions import BasePermission

from .constants import UserRole


class IsAdmin(BasePermission):
    """Allow access only for users with the admin role."""

    message = "Admin access required"

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == UserRole.ADMIN.value
        )
