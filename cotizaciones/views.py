from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Cotizacion
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os

# -----------------------------
# Dashboard
# -----------------------------
def dashboard(request):
    cotizaciones = Cotizacion.objects.all().order_by('-fecha')[:5]  # Últimas 5 cotizaciones
    context = {
        'cotizaciones': cotizaciones
    }
    return render(request, 'cotizaciones/dashboard.html', context)

# -----------------------------
# Listado de cotizaciones
# -----------------------------
def listado_cotizaciones(request):
    cotizaciones = Cotizacion.objects.all().order_by('-fecha')
    return render(request, 'cotizaciones/listado.html', {'cotizaciones': cotizaciones})

# -----------------------------
# Detalle de cotización
# -----------------------------
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    return render(request, 'cotizaciones/detalle.html', {'cotizacion': cotizacion})

# -----------------------------
# Generar PDF de cotización
# -----------------------------
def generar_pdf_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)

    # HttpResponse con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=18,
        spaceAfter=30, alignment=TA_CENTER, textColor=colors.darkblue
    )
    header_style = ParagraphStyle(
        'CustomHeader', parent=styles['Normal'], fontSize=12,
        spaceAfter=12, alignment=TA_CENTER, textColor=colors.darkblue
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=6
    )

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 12))

    # Header empresa
    company_data = [
        [Paragraph('<b>SERVICIOS INFORMÁTICOS</b>', header_style)],
        [Paragraph('Dilkendein 1278 - Tel: 358-4268768', normal_style)],
    ]
    company_table = Table(company_data, colWidths=[6*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 20))

    # Título
    title = f"{cotizacion.get_tipo_documento_display().upper()} N° {cotizacion.numero}"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))

    # Info cliente
    client_data = [
        ['Cliente:', cotizacion.cliente.nombre],
        ['Dirección:', cotizacion.cliente.direccion or 'No especificada'],
        ['Teléfono:', cotizacion.cliente.telefono or '-'],
        ['Localidad:', cotizacion.cliente.localidad or '-'],
        ['Fecha:', cotizacion.fecha.strftime('%d/%m/%Y')],
    ]
    client_table = Table(client_data, colWidths=[1.5*inch, 4.5*inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))

    # Tabla de productos
    if cotizacion.items.exists():
        table_data = [['Producto','Proveedor','Cantidad','Precio Unit.','Total']]
        for item in cotizacion.items.all():
            table_data.append([
                item.producto.nombre,
                item.producto.proveedor.nombre,
                str(item.cantidad),
                f'${item.precio_unitario:,.2f}',
                f'${item.subtotal:,.2f}'
            ])
        table_data.append(['', '', '', 'TOTAL:', f'${cotizacion.total:,.2f}'])

        items_table = Table(table_data, colWidths=[2*inch,1.5*inch,0.8*inch,1*inch,1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,0),10),
            ('FONTNAME',(0,1),(-1,-2),'Helvetica'),
            ('FONTSIZE',(0,1),(-1,-2),9),
            ('GRID',(0,0),(-1,-2),1,colors.black),
            ('BACKGROUND',(0,-1),(-1,-1),colors.lightgrey),
            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
            ('FONTSIZE',(0,-1),(-1,-1),11),
            ('ALIGN',(3,-1),(-1,-1),'RIGHT'),
        ]))
        elements.append(items_table)

    # Observaciones
    if cotizacion.observaciones:
        elements.append(Spacer(1,20))
        elements.append(Paragraph('<b>Observaciones:</b>', normal_style))
        elements.append(Paragraph(cotizacion.observaciones, normal_style))

    # Footer
    elements.append(Spacer(1,30))
    footer_text = "Paso a paso se llega lejos - GCSoft-2025 🏆🥇"
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer', parent=styles['Normal'], fontSize=8,
        alignment=TA_CENTER, textColor=colors.grey
    )))

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
