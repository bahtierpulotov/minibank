from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    is_blocked = models.BooleanField(default=False, help_text="User is blocked from making transfers")
    blocked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"