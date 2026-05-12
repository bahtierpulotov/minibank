from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Wallet, BankCard
from customers.serializers import UserShortSerializer


class WalletSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    balance_display = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'user_id', 'wallet_number', 'balance', 'balance_display',
            'currency', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['wallet_number', 'balance', 'created_at', 'updated_at']

    def get_balance_display(self, obj):
        return f"{obj.balance} {obj.currency}"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['balance'] = f"{instance.balance} {instance.currency}"
        rep['status_display'] = dict(Wallet.STATUS_CHOICES).get(instance.status, instance.status)
        return rep

    def validate_currency(self, value):
        if value not in ['TJS', 'USD', 'RUB']:
            raise serializers.ValidationError("Асъор бояд TJS, USD ё RUB бошад")
        return value

    def validate_status(self, value):
        if value not in ['ACTIVE', 'BLOCKED', 'CLOSED']:
            raise serializers.ValidationError("Статуси нодуруст")
        return value


class BankCardSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = BankCard
        fields = [
            'id', 'user', 'user_id', 'card_holder', 'masked_pan',
            'card_type', 'expire_month', 'expire_year', 'status', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_expire_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Моҳ бояд аз 1 то 12 бошад")
        return value

    def validate_expire_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < current_year:
            raise serializers.ValidationError("Соли анҷоми эътибор набояд гузашта бошад")
        return value

    def validate_masked_pan(self, value):
        if not value:
            raise serializers.ValidationError("masked_pan холӣ набошад")
        parts = value.split()
        if len(parts) != 4 or any(len(p) != 4 for p in parts[:-1]) or len(parts[-1]) != 4:
            raise serializers.ValidationError("Формат бояд **** **** **** 1234 бошад")
        return value

    def validate_card_holder(self, value):
        if not value:
            raise serializers.ValidationError("card_holder холӣ набошад")
        return value