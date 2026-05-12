from rest_framework.routers import DefaultRouter
from .views import FavoritePaymentViewSet
router = DefaultRouter()
router.register(r'', FavoritePaymentViewSet, basename='favorite')
urlpatterns = router.urls