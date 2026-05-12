from django.urls import path
from .views import payment_category_list, payment_category_detail
urlpatterns = [
    path('', payment_category_list, name='payment-category-list'),
    path('<int:pk>/', payment_category_detail, name='payment-category-detail'),
]