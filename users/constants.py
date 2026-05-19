from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""

    USER = "user"
    ADMIN = "admin"

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]
