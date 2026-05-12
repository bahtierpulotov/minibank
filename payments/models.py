from django.db import models
from django.contrib.auth.models import User
from wallets.models import Wallet         
from transactions.models import Transaction 

class PaymentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE, related_name='providers')
    name = models.CharField(max_length=100)
    account_mask = models.CharField(max_length=50, blank=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='payments')
    account_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment to {self.provider.name} - {self.amount}"

class FavoritePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_payments')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='favorites')
    title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'provider', 'account_number']

    def __str__(self):
        return f"{self.title} - {self.provider.name}"