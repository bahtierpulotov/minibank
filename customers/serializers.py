from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerProfile

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'user_id', 'phone_number', 'birth_date',
            'address', 'passport_number', 'is_blocked', 'blocked_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_blocked', 'blocked_at']

    def validate_phone_number(self, value):
        if not value.startswith('+992') and not value.isdigit():
            raise serializers.ValidationError("Телефон бояд бо +992 ё рақамҳо оғоз шавад")
        return value

    def validate_passport_number(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError("Рақами шиноснома набояд камтар аз 6 рақам бошад")
        return value