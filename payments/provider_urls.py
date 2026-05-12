from rest_framework.routers import DefaultRouter
from .views import ServiceProviderViewSet
router = DefaultRouter()
router.register(r'', ServiceProviderViewSet, basename='provider')
urlpatterns = router.urls