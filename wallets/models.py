from django.db import models
from django.contrib.auth.models import User
import random

class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('TJS', 'Somoni'),
        ('USD', 'Dollar'),
        ('RUB', 'Ruble'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('BLOCKED', 'Blocked'),
        ('CLOSED', 'Closed'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    wallet_number = models.CharField(max_length=20, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TJS')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.wallet_number:
            self.wallet_number = f"992{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.wallet_number} - {self.user.username}"


class BankCard(models.Model):
    CARD_TYPES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('KORTI_MILLI', 'Korti Milli'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('BLOCKED', 'Blocked'),
        ('EXPIRED', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_holder = models.CharField(max_length=100)
    masked_pan = models.CharField(max_length=25)  # **** **** **** 1234
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    expire_month = models.IntegerField()
    expire_year = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.masked_pan} - {self.user.username}"