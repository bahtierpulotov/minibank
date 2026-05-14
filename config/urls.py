from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import AllowAny


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('customers.urls')),
    path('api/wallets/', include('wallets.urls')),
    path('api/cards/', include('wallets.card_urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/payment-categories/', include('payments.category_urls')),
    path('api/providers/', include('payments.provider_urls')),
    path('api/payments/', include('payments.payment_urls')),
    path('api/favorites/', include('payments.favorite_urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # Swagger (OpenAPI) documentation
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]