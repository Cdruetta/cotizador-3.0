from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.clientes.api import ClienteViewSet
from apps.productos.api import ProductoViewSet, get_producto_precio
from apps.ventas.api import CotizacionViewSet, CotizacionItemViewSet
from apps.facturacion.api import FacturaViewSet

router = DefaultRouter()
router.register(r"clientes", ClienteViewSet, basename="api-cliente")
router.register(r"productos", ProductoViewSet, basename="api-producto")
router.register(r"cotizaciones", CotizacionViewSet, basename="api-cotizacion")
router.register(r"detalles-cotizacion", CotizacionItemViewSet, basename="api-detalle")
router.register(r"facturas", FacturaViewSet, basename="api-factura")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("v3/", include(router.urls)),
    path("producto/<int:producto_id>/precio/", get_producto_precio, name="get_producto_precio"),
]
