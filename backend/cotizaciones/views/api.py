from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Producto


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

