from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Player


@admin.register(Player)
class PlayerAdmin(UserAdmin):
    list_display = ("email", "name", "is_staff")
    ordering = ("email",)
    search_fields = ("email", "name")
    fieldsets = (
        (None, {"fields": ("email", "name", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "name", "password1", "password2")}),
    )
