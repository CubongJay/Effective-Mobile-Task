from django.contrib import admin

from .models import Users


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at")
