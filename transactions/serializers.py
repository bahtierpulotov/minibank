from rest_framework import serializers
from decimal import Decimal
from django.contrib.auth.models import User
from .models import Transaction
from wallets.models import Wallet


class WalletNestedSerializer(serializers.Serializer):
    wallet_number = serializers.CharField()
    owner = serializers.CharField(source='user.username', read_only=True)


class TransactionSerializer(serializers.ModelSerializer):
    sender_wallet = WalletNestedSerializer(read_only=True)
    receiver_wallet = WalletNestedSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender_wallet', 'receiver_wallet', 'transaction_type',
            'amount', 'commission', 'total_amount', 'currency', 'status',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender_wallet', 'receiver_wallet', 'transaction_type', 'amount', 'commission', 'total_amount', 'currency', 'status', 'description', 'created_at', 'updated_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        type_map = {
            'TOP_UP': 'Пополнение',
            'TRANSFER': 'Интиқоли пул',
            'PAYMENT': 'Пардохт',
            'WITHDRAW': 'Снятие',
        }
        rep['transaction_type'] = type_map.get(instance.transaction_type, instance.transaction_type)
        rep['status'] = 'Иҷро шуд' if instance.status == 'SUCCESS' else instance.status
        rep['amount'] = f"{instance.amount} {instance.currency}"
        rep['commission'] = f"{instance.commission} {instance.currency}"
        rep['total_amount'] = f"{instance.total_amount} {instance.currency}"
        return rep


class TopUpSerializer(serializers.Serializer):
    wallet_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Маблағ бояд аз 0 калон бошад")
        return value

    def validate_wallet_id(self, value):
        try:
            wallet = Wallet.objects.get(id=value, status='ACTIVE')
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Ҳамён вуҷуд надорад ё ғайрифаъол аст")
        return value


class TransferSerializer(serializers.Serializer):
    sender_wallet_id = serializers.IntegerField()
    receiver_wallet_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Маблағ бояд аз 0 калон бошад")
        if value > Decimal('100000.00'):
            raise serializers.ValidationError("Маблағ аз 100,000 зиёд аст. Амалиёт рад шуд.")
        return value

    def validate(self, data):
        sender_wallet_id = data.get('sender_wallet_id')
        receiver_number = data.get('receiver_wallet_number')
        amount = data.get('amount')

        try:
            sender_wallet = Wallet.objects.select_for_update().get(id=sender_wallet_id, status='ACTIVE')
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"sender_wallet_id": "Ҳамёни фиристанда мавҷуд нест ё ғайрифаъол"})

        try:
            receiver_wallet = Wallet.objects.select_for_update().get(wallet_number=receiver_number, status='ACTIVE')
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"receiver_wallet_number": "Ҳамёни гиранда мавҷуд нест ё ғайрифаъол"})

        if sender_wallet.id == receiver_wallet.id:
            raise serializers.ValidationError("Шумо наметавонед ба ҳамёни худ пул фиристед")

        if sender_wallet.balance < amount:
            raise serializers.ValidationError({"amount": "Баланси ҳамён кифоя нест"})

        if hasattr(sender_wallet.user, 'profile') and sender_wallet.user.profile.is_blocked:
            raise serializers.ValidationError("Ҳисоби шумо блок шудааст. Амалиёт иҷро намешавад.")

        data['sender_wallet_obj'] = sender_wallet
        data['receiver_wallet_obj'] = receiver_wallet
        return data