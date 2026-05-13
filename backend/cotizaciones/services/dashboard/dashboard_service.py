from datetime import date
from decimal import Decimal

from django.db.models import Sum

from ...models import (
    Cliente,
    Proveedor,
    Producto,
    Cotizacion,
    Factura,
)

from ..system.db_usage import get_db_usage_percent


def build_dashboard_context():
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    db_percent, db_mb, db_max_mb = get_db_usage_percent()

    total_facturado = (
        Factura.objects.filter(
            fecha__gte=inicio_mes,
            estado="autorizada",
        ).aggregate(total=Sum("total"))["total"]
        or Decimal("0")
    )

    return {
        "total_clientes": Cliente.objects.count(),

        "total_proveedores": Proveedor.objects.count(),

        "total_productos": Producto.objects.filter(
            activo=True
        ).count(),

        "total_cotizaciones": Cotizacion.objects.count(),

        "cotizaciones_mes": Cotizacion.objects.filter(
            fecha__gte=inicio_mes
        ).count(),

        "cotizaciones_pendientes": Cotizacion.objects.exclude(
            estado="facturada"
        ).count(),

        "facturas_borrador": Factura.objects.filter(
            estado="borrador"
        ).count(),

        "total_facturado_mes": total_facturado,

        "cotizaciones_recientes": Cotizacion.objects.select_related(
            "cliente",
            "usuario",
        ).order_by("-fecha")[:5],

        "facturas_recientes": Factura.objects.select_related(
            "cliente",
            "usuario",
        ).order_by("-creada")[:5],

        "db_percent": db_percent,
        "db_mb": db_mb,
        "db_max_mb": db_max_mb,
    }