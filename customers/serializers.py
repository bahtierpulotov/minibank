from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomerProfile
from django.contrib.auth import authenticate


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
    
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Логин ё парол хатост!")
        data['user'] = user
        return data


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']