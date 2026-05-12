from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Wallet, BankCard
from .serializers import WalletSerializer, BankCardSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all().order_by('-created_at')
    serializer_class = WalletSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['currency', 'status']
    search_fields = ['wallet_number', 'user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['balance', 'created_at']


class BankCardViewSet(viewsets.ModelViewSet):
    queryset = BankCard.objects.all().order_by('-created_at')
    serializer_class = BankCardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['card_type', 'status']
    search_fields = ['masked_pan', 'card_holder']