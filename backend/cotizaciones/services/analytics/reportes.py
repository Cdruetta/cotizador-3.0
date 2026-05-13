import json
from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from ...models import Cotizacion, CotizacionItem


def build_reportes_context(request):
    hoy = date.today()

    def shift_month(year: int, month: int, delta_months: int):
        total = year * 12 + (month - 1) + delta_months
        new_year = total // 12
        new_month = total % 12 + 1
        return new_year, new_month

    meses = []
    base_y, base_m = hoy.year, hoy.month

    for i in range(5, -1, -1):
        y, m = shift_month(base_y, base_m, -i)

        inicio = date(y, m, 1)
        fin = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)

        meses.append({
            "key": f"{y:04d}-{m:02d}",
            "label": inicio.strftime("%b %Y"),
            "start": inicio,
            "end": fin,
        })

    mes_sel = request.GET.get("mes")

    mes_sel_obj = (
        next((m for m in meses if m["key"] == mes_sel), None)
        or meses[-1]
    )

    rango_inicio = mes_sel_obj["start"]
    rango_fin = mes_sel_obj["end"]

    # ─────────────────────────────────────────────
    # Ventas por mes (solo facturadas)
    # ─────────────────────────────────────────────

    ventas_qs = (
        Cotizacion.objects.filter(
            fecha__gte=meses[0]["start"],
            fecha__lt=meses[-1]["end"],
            estado="facturada",
        )
        .annotate(mes=TruncMonth("fecha"))
        .values("mes")
        .annotate(
            total=Sum("total"),
            cantidad=Count("id"),
        )
        .order_by("mes")
    )

    ventas_map = {
        (row["mes"].year, row["mes"].month): row
        for row in ventas_qs
    }

    ventas_mes = []

    for m in meses:
        key = (m["start"].year, m["start"].month)
        row = ventas_map.get(key)

        ventas_mes.append({
            "mes": m["label"],
            "total": float(row["total"]) if row else 0,
            "cantidad": row["cantidad"] if row else 0,
        })

    # ─────────────────────────────────────────────
    # Facturación y cotizaciones
    # ─────────────────────────────────────────────

    facturado_mes = (
        Cotizacion.objects.filter(
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
            estado="facturada",
        ).aggregate(t=Sum("total"))["t"]
        or 0
    )

    monto_cotizado_mes = (
        Cotizacion.objects.filter(
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).aggregate(t=Sum("total"))["t"]
        or 0
    )

    # ─────────────────────────────────────────────
    # Top clientes
    # ─────────────────────────────────────────────

    top_clientes = (
        Cotizacion.objects.filter(
            estado="facturada",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        )
        .values("cliente__nombre")
        .annotate(
            total=Sum("total"),
            cantidad=Count("id"),
        )
        .order_by("-total")[:5]
    )

    # ─────────────────────────────────────────────
    # Top productos
    # ─────────────────────────────────────────────

    top_productos = (
        CotizacionItem.objects.filter(
            cotizacion__estado="facturada",
            cotizacion__fecha__gte=rango_inicio,
            cotizacion__fecha__lt=rango_fin,
        )
        .values("producto__nombre")
        .annotate(
            veces=Count("id"),
            total_vendido=Sum("subtotal"),
        )
        .order_by("-veces")[:5]
    )

    # ─────────────────────────────────────────────
    # Estados de cotizaciones
    # ─────────────────────────────────────────────

    estado_data = {
        "borrador": Cotizacion.objects.filter(
            estado="borrador",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),

        "enviadas": Cotizacion.objects.filter(
            estado="enviada",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),

        "aprobadas": Cotizacion.objects.filter(
            estado="aprobada",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),

        "rechazadas": Cotizacion.objects.filter(
            estado="rechazada",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),

        "facturadas": Cotizacion.objects.filter(
            estado="facturada",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),
    }

    # ─────────────────────────────────────────────
    # Tipos de documento
    # ─────────────────────────────────────────────

    tipo_data = {
        "presupuestos": Cotizacion.objects.filter(
            tipo_documento="presupuesto",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),

        "recibos": Cotizacion.objects.filter(
            tipo_documento="recibo",
            fecha__gte=rango_inicio,
            fecha__lt=rango_fin,
        ).count(),
    }

    return {
        "mes_options": meses,
        "mes_selected_key": mes_sel_obj["key"],
        "mes_selected_label": mes_sel_obj["label"],

        "ventas_mes_json": json.dumps(ventas_mes),

        "top_clientes_json": json.dumps([
            {
                "nombre": c["cliente__nombre"],
                "total": float(c["total"]),
                "cantidad": c["cantidad"],
            }
            for c in top_clientes
        ]),

        "top_productos_json": json.dumps([
            {
                "nombre": p["producto__nombre"],
                "veces": p["veces"],
                "total": float(p["total_vendido"]),
            }
            for p in top_productos
        ]),

        "estado_json": json.dumps(estado_data),
        "tipo_json": json.dumps(tipo_data),

        "facturado_mes": facturado_mes,
        "monto_cotizado_mes": monto_cotizado_mes,
    }