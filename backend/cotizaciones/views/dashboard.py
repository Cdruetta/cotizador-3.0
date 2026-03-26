from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from ..models import Cliente, Proveedor, Producto, Cotizacion
from ..services.system.db_usage import get_db_usage_percent
from ..services.analytics.reportes import build_reportes_context


@login_required
def dashboard(request):
    db_percent, db_mb, db_max_mb = get_db_usage_percent()
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    context = {
        "total_clientes": Cliente.objects.count(),
        "total_proveedores": Proveedor.objects.count(),
        "total_productos": Producto.objects.filter(activo=True).count(),
        "total_cotizaciones": Cotizacion.objects.count(),
        "cotizaciones_mes": Cotizacion.objects.filter(fecha__gte=inicio_mes).count(),
        "total_facturado_mes": Cotizacion.objects.filter(
            fecha__gte=inicio_mes, completada=True
        ).aggregate(t=Sum("total"))["t"]
        or Decimal("0"),
        "cotizaciones_pendientes": Cotizacion.objects.filter(completada=False).count(),
        "cotizaciones_recientes": Cotizacion.objects.select_related("cliente", "usuario")[:5],
        "db_percent": db_percent,
        "db_mb": db_mb,
        "db_max_mb": db_max_mb,
    }
    return render(request, "cotizaciones/dashboard.html", context)


@login_required
def reportes(request):
    context = build_reportes_context(request)
    return render(request, "cotizaciones/reportes.html", context)

