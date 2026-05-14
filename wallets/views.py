from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Wallet, BankCard
from .serializers import WalletSerializer, BankCardSerializer
from customers.permissions import IsOwnerOrAdmin


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['currency', 'status']
    search_fields = ['wallet_number', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['balance', 'created_at']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Wallet.objects.all().order_by('-created_at')
        return Wallet.objects.filter(user=self.request.user).order_by('-created_at')


class BankCardViewSet(viewsets.ModelViewSet):
    serializer_class = BankCardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['card_type', 'status']
    search_fields = ['masked_pan', 'card_holder']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BankCard.objects.all().order_by('-created_at')
        return BankCard.objects.filter(user=self.request.user).order_by('-created_at')