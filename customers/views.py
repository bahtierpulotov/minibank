from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from .models import CustomerProfile
from .serializers import CustomerProfileSerializer, RegisterSerializer, LoginSerializer, UserMeSerializer
from .permissions import IsOwnerOrAdmin


class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomerProfile.objects.all().order_by('-created_at')
        return CustomerProfile.objects.filter(user=user)


@extend_schema(tags=['auth'])
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['auth'])
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserMeSerializer}
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": UserMeSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error": "Логин ё парол хатост!"}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(tags=['auth'])
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Шумо баромадед!"}, status=status.HTTP_200_OK)