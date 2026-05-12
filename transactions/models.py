from django.db import models
from wallets.models import Wallet


class Transaction(models.Model):
    TXN_TYPES = [
        ('TOP_UP', 'Пополнение'),
        ('TRANSFER', 'Перевод'),
        ('PAYMENT', 'Платеж'),
        ('WITHDRAW', 'Снятие'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'В ожидании'),
        ('SUCCESS', 'Успешно'),
        ('FAILED', 'Ошибка'),
        ('CANCELLED', 'Отменен'),
    ]

    sender_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE,
        related_name='sent_transactions', null=True, blank=True
    )
    receiver_wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE,
        related_name='received_transactions', null=True, blank=True
    )
    transaction_type = models.CharField(max_length=20, choices=TXN_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='TJS')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.status})"