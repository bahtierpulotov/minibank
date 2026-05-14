from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CustomerProfileViewSet, RegisterAPIView, LoginAPIView, LogoutAPIView

router = DefaultRouter()
router.register(r'profiles', CustomerProfileViewSet, basename='profile')

urlpatterns = router.urls + [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]