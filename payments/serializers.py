from rest_framework import serializers
from decimal import Decimal
from django.contrib.auth.models import User
from wallets.models import Wallet
from .models import PaymentCategory, ServiceProvider, Payment, FavoritePayment
from customers.serializers import UserShortSerializer

class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']

class ServiceProviderSerializer(serializers.ModelSerializer):
    category = PaymentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = ServiceProvider
        fields = ['id', 'category', 'category_id', 'name', 'account_mask',
                  'min_amount', 'max_amount', 'commission_percent', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def validate_min_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("min_amount набояд манфӣ бошад")
        return value

    def validate_max_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("max_amount бояд аз 0 калон бошад")
        return value

    def validate(self, data):
        if data.get('min_amount', 0) > data.get('max_amount', 0):
            raise serializers.ValidationError("min_amount набояд аз max_amount калон бошад")
        return data

class PaymentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    wallet = serializers.StringRelatedField(read_only=True)
    wallet_id = serializers.PrimaryKeyRelatedField(
        queryset=Wallet.objects.all(), source='wallet', write_only=True
    )
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(), source='provider', write_only=True
    )
    total_amount_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_id', 'wallet', 'wallet_id', 'provider', 'provider_id',
            'account_number', 'amount', 'commission', 'total_amount', 'total_amount_display',
            'status', 'status_display', 'transaction', 'created_at'
        ]
        read_only_fields = ['commission', 'total_amount', 'status', 'transaction', 'created_at']

    def get_total_amount_display(self, obj):
        return f"{obj.total_amount} TJS"

    def get_status_display(self, obj):
        return dict(Payment.STATUS_CHOICES).get(obj.status, obj.status)

    def validate_account_number(self, value):
        if not value:
            raise serializers.ValidationError("account_number холӣ набошад")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Маблағ бояд аз 0 калон бошад")
        return value

    def validate(self, data):
        provider = data.get('provider')
        amount = data.get('amount')
        wallet = data.get('wallet')

        if not provider.is_active:
            raise serializers.ValidationError({"provider_id": "Ин провайдер ғайрифаъол аст"})

        if amount < provider.min_amount:
            raise serializers.ValidationError({"amount": f"Маблағ набояд аз {provider.min_amount} камтар бошад"})
        if amount > provider.max_amount:
            raise serializers.ValidationError({"amount": f"Маблағ набояд аз {provider.max_amount} зиёд бошад"})

        commission = amount * (provider.commission_percent / Decimal('100'))
        total_amount = amount + commission

        if wallet.balance < total_amount:
            raise serializers.ValidationError({"wallet_id": "Баланси ҳамён барои пардохт кифоя нест"})

        data['commission'] = commission
        data['total_amount'] = total_amount
        return data

class FavoritePaymentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    provider = ServiceProviderSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(), source='provider', write_only=True
    )

    class Meta:
        model = FavoritePayment
        fields = ['id', 'user', 'user_id', 'provider', 'provider_id', 'title', 'account_number', 'created_at']
        read_only_fields = ['created_at']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title холӣ набошад")
        return value

    def validate_account_number(self, value):
        if not value:
            raise serializers.ValidationError("account_number холӣ набошад")
        return value

    def validate_provider_id(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Провайдер ғайрифаъол аст")
        return value