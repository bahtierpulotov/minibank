from django.urls import path
from .views import PaymentListCreateAPIView, PaymentRetrieveAPIView
urlpatterns = [
    path('', PaymentListCreateAPIView.as_view(), name='payment-list-create'),
    path('<int:pk>/', PaymentRetrieveAPIView.as_view(), name='payment-detail'),
]