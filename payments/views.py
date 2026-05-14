from rest_framework import status, viewsets, generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction as db_transaction
from decimal import Decimal

from .models import PaymentCategory, ServiceProvider, Payment, FavoritePayment
from .serializers import (
    PaymentCategorySerializer, ServiceProviderSerializer,
    PaymentSerializer, FavoritePaymentSerializer
)
from transactions.models import Transaction
from wallets.models import Wallet
from notifications.models import Notification
from customers.permissions import IsAdminOrReadOnly


@api_view(['GET', 'POST'])
def payment_category_list(request):
    if request.method == 'GET':
        categories = PaymentCategory.objects.filter(is_active=True)
        serializer = PaymentCategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_superuser:
            return Response({"error": "Танҳо Admin иловаи категория карда метавонад"}, status=403)
        serializer = PaymentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
def payment_category_detail(request, pk):
    try:
        category = PaymentCategory.objects.get(pk=pk)
    except PaymentCategory.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentCategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if not request.user.is_superuser:
            return Response({"error": "Танҳо Admin тағйир дода метавонад"}, status=403)
        serializer = PaymentCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_superuser:
            return Response({"error": "Танҳо Admin тағйир дода метавонад"}, status=403)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all().order_by('name')
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'min_amount', 'max_amount']


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'provider', 'wallet']
    search_fields = ['account_number', 'provider__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all().order_by('-created_at')
        return Payment.objects.filter(user=user).order_by('-created_at')

    @db_transaction.atomic
    def perform_create(self, serializer):
        data = serializer.validated_data
        user = data['user']
        wallet = data['wallet']
        provider = data['provider']
        account_number = data['account_number']
        amount = data['amount']
        commission = data.get('commission', Decimal('0.00'))
        total_amount = data.get('total_amount', amount + commission)

        wallet.balance -= total_amount
        wallet.save()

        payment = serializer.save(
            commission=commission,
            total_amount=total_amount,
            status='SUCCESS'
        )

        transaction_obj = Transaction.objects.create(
            sender_wallet=wallet,
            transaction_type='PAYMENT',
            amount=amount,
            commission=commission,
            total_amount=total_amount,
            currency=wallet.currency,
            status='SUCCESS',
            description=f"Пардохт ба {provider.name} ({account_number})"
        )
        payment.transaction = transaction_obj
        payment.save(update_fields=['transaction'])

        Notification.objects.create(
            user=user,
            title="Пардохт анҷом шуд",
            message=f"Шумо {total_amount} {wallet.currency} ба {provider.name} ({account_number}) пардохт кардед.",
            notification_type='PAYMENT'
        )


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class FavoritePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritePaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider']
    search_fields = ['title', 'account_number', 'provider__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return FavoritePayment.objects.all().order_by('-created_at')
        return FavoritePayment.objects.filter(user=user).order_by('-created_at')