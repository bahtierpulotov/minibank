from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Transaction
from .serializers import TransactionSerializer, TopUpSerializer, TransferSerializer
from wallets.models import Wallet
from notifications.models import Notification


class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction_type', 'currency', 'sender_wallet', 'receiver_wallet']
    search_fields = ['description', 'sender_wallet__wallet_number', 'receiver_wallet__wallet_number']
    ordering_fields = ['amount', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Transaction.objects.all().order_by('-created_at')
        return (
            Transaction.objects.filter(sender_wallet__user=user) |
            Transaction.objects.filter(receiver_wallet__user=user)
        ).order_by('-created_at')


class TransactionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Transaction.objects.all()
        return (
            Transaction.objects.filter(sender_wallet__user=user) |
            Transaction.objects.filter(receiver_wallet__user=user)
        )


class TopUpAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TopUpSerializer,
        responses={200: TransactionSerializer}
    )
    @db_transaction.atomic
    def post(self, request):
        serializer = TopUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        wallet_id = data['wallet_id']
        amount = data['amount']
        description = data.get('description', '')

        try:
            wallet = Wallet.objects.select_for_update().get(id=wallet_id, status='ACTIVE')
        except Wallet.DoesNotExist:
            return Response({"error": "Ҳамён мавҷуд нест ё ғайрифаъол"}, status=status.HTTP_404_NOT_FOUND)

        wallet.balance += amount
        wallet.save()

        transaction_obj = Transaction.objects.create(
            receiver_wallet=wallet,
            transaction_type='TOP_UP',
            amount=amount,
            commission=Decimal('0.00'),
            total_amount=amount,
            currency=wallet.currency,
            status='SUCCESS',
            description=description
        )

        Notification.objects.create(
            user=wallet.user,
            title="Пуркунии ҳамён",
            message=f"Ҳамёни шумо бо маблағи {amount} {wallet.currency} пур карда шуд.",
            notification_type='TRANSACTION'
        )

        return Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_200_OK)


class TransferAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TransferSerializer,
        responses={200: TransactionSerializer}
    )
    @db_transaction.atomic
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        sender_wallet = data['sender_wallet_obj']
        receiver_wallet = data['receiver_wallet_obj']
        amount = data['amount']
        description = data.get('description', '')

        if amount > Decimal('100000.00'):
            profile = sender_wallet.user.profile
            profile.is_blocked = True
            profile.blocked_at = timezone.now()
            profile.save()
            return Response(
                {"error": "Маблағ аз 100,000 зиёд аст. Ҳисоби шумо блок шуд."},
                status=status.HTTP_403_FORBIDDEN
            )

        sender_wallet.balance -= amount
        receiver_wallet.balance += amount
        sender_wallet.save()
        receiver_wallet.save()

        transaction_obj = Transaction.objects.create(
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
            transaction_type='TRANSFER',
            amount=amount,
            commission=Decimal('0.00'),
            total_amount=amount,
            currency=sender_wallet.currency,
            status='SUCCESS',
            description=description
        )

        Notification.objects.create(
            user=sender_wallet.user,
            title="Интиқоли пул",
            message=f"Шумо {amount} {sender_wallet.currency} ба {receiver_wallet.wallet_number} фиристодед.",
            notification_type='TRANSACTION'
        )
        Notification.objects.create(
            user=receiver_wallet.user,
            title="Воридшавии пул",
            message=f"Ба ҳамёни шумо {amount} {receiver_wallet.currency} аз {sender_wallet.wallet_number} ворид шуд.",
            notification_type='TRANSACTION'
        )

        return Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_200_OK)