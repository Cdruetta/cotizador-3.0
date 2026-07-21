from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Producto
from .serializers import ProductoSerializer
from apps.core.api import EsAdministradorOReadOnly


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "activo", "proveedor"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio_unitario", "stock", "nombre"]


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
