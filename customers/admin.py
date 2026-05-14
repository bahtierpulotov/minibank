from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomerProfile

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_number', 'is_blocked', 'created_at']
    search_fields = ['user__username', 'phone_number']
    list_filter = ['is_blocked']