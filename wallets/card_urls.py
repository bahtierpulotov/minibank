from rest_framework.routers import DefaultRouter
from .views import BankCardViewSet

router = DefaultRouter()
router.register(r'', BankCardViewSet, basename='card')

urlpatterns = router.urls