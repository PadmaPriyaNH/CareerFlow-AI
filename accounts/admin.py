
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_mfa_enabled', 'created_at')
    search_fields = ('user__username', 'phone_number')
