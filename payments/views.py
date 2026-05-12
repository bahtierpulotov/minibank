from rest_framework import status, viewsets, generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
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

# ---------- PaymentCategory CBV (Function-Based Views) ----------
@api_view(['GET', 'POST'])
def payment_category_list(request):
    if request.method == 'GET':
        categories = PaymentCategory.objects.filter(is_active=True)
        serializer = PaymentCategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
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
        serializer = PaymentCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ---------- ServiceProvider ViewSet ----------
class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all().order_by('name')
    serializer_class = ServiceProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'min_amount', 'max_amount']

# ---------- Payment List/Create (GenericAPIView) ----------
class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'provider', 'wallet']
    search_fields = ['account_number', 'provider__name']

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

        # Аз баланс кам кардан
        wallet.balance -= total_amount
        wallet.save()

        # Эҷоди Payment
        payment = serializer.save(
            commission=commission,
            total_amount=total_amount,
            status='SUCCESS'
        )

        # Эҷоди Transaction
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

        # Огоҳинома
        Notification.objects.create(
            user=user,
            title="Пардохт анҷом шуд",
            message=f"Шумо {total_amount} {wallet.currency} ба {provider.name} ({account_number}) пардохт кардед.",
            notification_type='PAYMENT'
        )

class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# ---------- FavoritePayment ViewSet ----------
class FavoritePaymentViewSet(viewsets.ModelViewSet):
    queryset = FavoritePayment.objects.all().order_by('-created_at')
    serializer_class = FavoritePaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider']
    search_fields = ['title', 'account_number', 'provider__name']