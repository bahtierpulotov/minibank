from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all().order_by('-created_at')
    serializer_class = CustomerProfileSerializer

    def perform_create(self, serializer):
        serializer.save()