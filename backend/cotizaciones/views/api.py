from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# 📦 IMPORTACIONES DE MODELOS
from ..models import Cliente, Cotizacion, CotizacionItem, Factura, Producto

# 🧪 IMPORTACIONES DE SERIALIZERS
from ..serializers import (
    ClienteSerializer, 
    CotizacionSerializer, 
    CotizacionItemSerializer,
    FacturaSerializer, 
    ProductoSerializer
)

# ==============================================================================
# 🛠️ 1. TU FUNCIÓN ACTUAL (Mantenida intacta para compatibilidad)
# ==============================================================================
@login_required
def get_producto_precio(request, producto_id):
    try:
        producto = Producto.objects.select_related("proveedor").get(id=producto_id)
        return JsonResponse(
            {
                "precio": float(producto.precio_unitario),
                "nombre": producto.nombre,
                "proveedor": producto.proveedor.nombre,
                "stock": producto.stock,
            }
        )
    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)


# ==============================================================================
# 🛡️ 2. SISTEMA DE PERMISOS Y ROLES
# ==============================================================================
class EsAdministradorOReadOnly(permissions.BasePermission):
    """
    Seguridad del Backend: 
    - Usuarios comunes autenticados mediante JWT solo leen (GET).
    - Administradores (is_staff=True) pueden Crear, Modificar y Borrar (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ==============================================================================
# 🚀 3. ENDPOINTS CRUD COMPLETOS CON FILTROS SEGUROS PARA SWAGGER
# ==============================================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # ✨ Limpio de 'condicion_iva'
    filterset_fields = [] 
    search_fields = ['razon_social', 'cuit', 'email', 'telefono']
    ordering_fields = ['razon_social', 'id']


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # ✨ Quitamos el filtro exacto por objeto para evitar conflictos de introspección
    filterset_fields = [] 
    search_fields = ['codigo', 'nombre', 'descripcion', 'marca']
    ordering_fields = ['precio_unitario', 'stock', 'nombre']


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtro nativo por estado (ej: ?estado=Borrador o ?estado=Aprobada)
    filterset_fields = ['estado'] 
    search_fields = ['nro_cotizacion', 'observaciones', 'cliente__razon_social']
    ordering_fields = ['fecha', 'total', 'id']
    ordering = ['-fecha']


class CotizacionItemViewSet(viewsets.ModelViewSet):
    queryset = CotizacionItem.objects.all()
    serializer_class = CotizacionItemSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = []


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # ✨ CORREGIDO: Eliminamos 'estado_pago' y 'cotizacion' que hacían explotar el backend
    filterset_fields = [] 
    search_fields = ['nro_factura', 'cae', 'cotizacion__nro_cotizacion']
    ordering_fields = ['fecha_emision', 'id']