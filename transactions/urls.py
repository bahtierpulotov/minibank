from django.urls import path
from .views import (
    TransactionListAPIView, TransactionDetailAPIView,
    TopUpAPIView, TransferAPIView
)

urlpatterns = [
    path('', TransactionListAPIView.as_view(), name='transaction-list'),
    path('<int:pk>/', TransactionDetailAPIView.as_view(), name='transaction-detail'),
    path('top-up/', TopUpAPIView.as_view(), name='top-up'),
    path('transfer/', TransferAPIView.as_view(), name='transfer'),
]