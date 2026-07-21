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

    # Ventas de hoy
    facturas_hoy = Factura.objects.filter(fecha=hoy)
    ventas_hoy = facturas_hoy.filter(estado="autorizada").aggregate(total=Sum("total"))["total"] or Decimal("0")
    transacciones_hoy = facturas_hoy.filter(estado="autorizada").count()

    # Ventas del mes
    facturas_mes = Factura.objects.filter(fecha__gte=inicio_mes)
    ventas_mes = facturas_mes.filter(estado="autorizada").aggregate(total=Sum("total"))["total"] or Decimal("0")
    transacciones_mes = facturas_mes.filter(estado="autorizada").count()

    # Cantidad de productos activos
    cantidad_productos = Producto.objects.filter(activo=True).count()

    # Clientes activos (total de clientes)
    clientes_activos = Cliente.objects.count()
    leads_progreso = 0

    # Cotizaciones recientes
    cotizaciones_recientes = Cotizacion.objects.select_related(
        "cliente",
        "usuario",
    ).order_by("-fecha")[:5]

    # Facturas recientes de hoy
    facturas_recientes_hoy = facturas_hoy.select_related("cliente").order_by("-fecha")[:10]

    return {
        "ventas_hoy": ventas_hoy,
        "transacciones_hoy": transacciones_hoy,
        "ventas_mes": ventas_mes,
        "transacciones_mes": transacciones_mes,
        "cantidad_productos": cantidad_productos,
        "clientes_activos": clientes_activos,
        "leads_progreso": leads_progreso,
        "cotizaciones_recientes": cotizaciones_recientes,
        "facturas_recientes_hoy": facturas_recientes_hoy,
    }

