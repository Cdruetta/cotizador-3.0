from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importamos las clases directo desde el archivo api.py
from cotizaciones.views.api import (
    ClienteViewSet, 
    ProductoViewSet, 
    CotizacionViewSet, 
    CotizacionItemViewSet, 
    FacturaViewSet,
    get_producto_precio
)

# Registramos en el router exclusivo de la API
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='api-cliente')
router.register(r'productos', ProductoViewSet, basename='api-producto')
router.register(r'cotizaciones', CotizacionViewSet, basename='api-cotizacion')
router.register(r'detalles-cotizacion', CotizacionItemViewSet, basename='api-detalle')
router.register(r'facturas', FacturaViewSet, basename='api-factura')

urlpatterns = [
    # Autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints CRUD automáticos bajo api/v3/
    path('v3/', include(router.urls)),
    
    # Endpoint antiguo mantenido por compatibilidad
    path('producto/<int:producto_id>/precio/', get_producto_precio, name='get_producto_precio'),
]