from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
import calendar
from datetime import timedelta

from ..models.facturacion import Factura
from ..models.cotizaciones import Cotizacion, CotizacionItem

@login_required
def reportes_view(request):
    # --- 1. Lógica de Selección de Mes ---
    hoy = timezone.now()
    mes_selected_key = request.GET.get('mes', f"{hoy.year}-{hoy.month:02d}")
    
    mes_options = []
    for i in range(12):
        first_of_month = (hoy.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        mes_options.append({
            'key': first_of_month.strftime("%Y-%m"),
            'label': f"{calendar.month_name[first_of_month.month].capitalize()} {first_of_month.year}"
        })

    try:
        sel_year, sel_month = map(int, mes_selected_key.split('-'))
    except ValueError:
        sel_year, sel_month = hoy.year, hoy.month

    mes_selected_label = f"{calendar.month_name[sel_month].capitalize()} {sel_year}"

    # --- 2. KPIs del Mes Seleccionado ---
    # Facturado
    facturado_qs = Factura.objects.filter(
        fecha__year=sel_year, 
        fecha__month=sel_month, 
        estado='autorizada'
    )
    facturado_mes = facturado_qs.aggregate(total=Sum('total'))['total'] or 0
    conteo_facturas = facturado_qs.count()

    # Ticket Promedio
    ticket_promedio = facturado_mes / conteo_facturas if conteo_facturas > 0 else 0
    
    # Cotizado
    cotizaciones_qs = Cotizacion.objects.filter(
        fecha__year=sel_year, 
        fecha__month=sel_month
    )
    monto_cotizado_mes = cotizaciones_qs.aggregate(total=Sum('total'))['total'] or 0
    cotizaciones_mes_count = cotizaciones_qs.count()

    # TASA DE CIERRE (Lógica simplificada a prueba de errores)
    # Si no hay relación directa, comparamos volumen de éxito vs volumen de intentos
    tasa_cierre = (conteo_facturas / cotizaciones_mes_count * 100) if cotizaciones_mes_count > 0 else 0

    # Pendientes
    cotizaciones_pendientes = Cotizacion.objects.filter(estado='pendiente').count()

    # --- 3. Histórico de Ventas (Últimos 6 meses) ---
    labels_6_meses = []
    data_6_meses = []
    for i in range(5, -1, -1):
        f_iter = (hoy.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        monto = Factura.objects.filter(
            fecha__year=f_iter.year, 
            fecha__month=f_iter.month, 
            estado='autorizada'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        labels_6_meses.append(calendar.month_name[f_iter.month].capitalize()[:3])
        data_6_meses.append(float(monto))

    # --- 4. Datos para Gráficos ---
    top_clientes = facturado_qs.values('cliente__nombre').annotate(
        total=Sum('total')).order_by('-total')[:5]
    
    top_productos = CotizacionItem.objects.filter(
        cotizacion__fecha__year=sel_year, 
        cotizacion__fecha__month=sel_month
    ).values('producto__nombre').annotate(
        total=Count('id')).order_by('-total')[:5]

    estados_data = cotizaciones_qs.values('estado').annotate(count=Count('id'))

    context = {
        'mes_options': mes_options,
        'mes_selected_key': mes_selected_key,
        'mes_selected_label': mes_selected_label,
        'facturado_mes': facturado_mes,
        'monto_cotizado_mes': monto_cotizado_mes,
        'cotizaciones_mes': cotizaciones_mes_count,
        'cotizaciones_pendientes': cotizaciones_pendientes,
        'ticket_promedio': ticket_promedio,
        'tasa_cierre': round(min(tasa_cierre, 100), 1), # Limitamos a 100% para que sea lógico
        
        'labels_6_meses': labels_6_meses,
        'data_6_meses': data_6_meses,
        'chart_clientes_labels': [c['cliente__nombre'] for c in top_clientes],
        'chart_clientes_data': [float(c['total']) for c in top_clientes],
        'chart_productos_labels': [p['producto__nombre'] for p in top_productos],
        'chart_productos_data': [p['total'] for p in top_productos],
        'chart_estado_labels': [e['estado'].capitalize() for e in estados_data],
        'chart_estado_data': [e['count'] for e in estados_data],
    }

    return render(request, 'cotizaciones/reportes.html', context)