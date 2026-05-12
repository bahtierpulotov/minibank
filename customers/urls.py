
from rest_framework.routers import DefaultRouter
from .views import CustomerProfileViewSet

router = DefaultRouter()
router.register(r'', CustomerProfileViewSet, basename='profile')

urlpatterns = router.urls