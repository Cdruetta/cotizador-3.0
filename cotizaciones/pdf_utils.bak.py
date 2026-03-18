from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse
from django.conf import settings
import os
from io import BytesIO
from decimal import Decimal


def _build_elements(cotizacion):
    """Construye los elementos del PDF y retorna (elements, styles)."""
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', fontSize=18, alignment=TA_CENTER,
                                  textColor=colors.darkblue, spaceAfter=20)
    normal_style = ParagraphStyle('Normal', fontSize=10, leading=12, spaceAfter=6)
    table_cell_style = ParagraphStyle('TableCell', fontSize=9, leading=11)
    right_style = ParagraphStyle('Right', fontSize=9, leading=11, alignment=TA_RIGHT)

    elements = []

    # Logo + empresa
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    logo_img = None
    if os.path.exists(logo_path):
        img_reader = ImageReader(logo_path)
        img_w, img_h = img_reader.getSize()
        desired_w = 1.4 * inch
        logo_img = Image(logo_path, width=desired_w, height=desired_w * (img_h / img_w))
        logo_img.hAlign = 'CENTER'

    company_table = Table(
        [[logo_img or '', Paragraph(
            '<font size=12><b>GCinsumos</b></font><br/><b>SERVICIOS INFORMÁTICOS</b>'
            '<br/><font size=10>Dilkendein 1278 - Tel: 358-4268768</font>', normal_style
        )]],
        colWidths=[1.7 * inch, 4.3 * inch]
    )
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(str(cotizacion.numero), title_style))

    # Datos del cliente
    client_data = [
        ['Cliente:', cotizacion.cliente.nombre],
        ['Dirección:', cotizacion.cliente.direccion or 'No especificada'],
        ['Teléfono:', cotizacion.cliente.telefono or '-'],
        ['Localidad:', cotizacion.cliente.localidad or '-'],
        ['Fecha:', cotizacion.fecha.strftime('%d/%m/%Y')],
    ]
    client_table = Table(client_data, colWidths=[1.5 * inch, 4.5 * inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))

    # Tabla de productos
    if cotizacion.items.exists():
        table_data = [[
            Paragraph('<b>Producto</b>', table_cell_style),
            Paragraph('<b>Proveedor</b>', table_cell_style),
            Paragraph('<b>Cant.</b>', table_cell_style),
            Paragraph('<b>Precio Unit.</b>', table_cell_style),
            Paragraph('<b>Total</b>', table_cell_style),
        ]]
        for item in cotizacion.items.all():
            table_data.append([
                Paragraph(item.producto.nombre, table_cell_style),
                Paragraph(item.producto.proveedor.nombre, table_cell_style),
                Paragraph(str(item.cantidad), table_cell_style),
                Paragraph(f'${item.precio_unitario:,.2f}', right_style),
                Paragraph(f'${item.subtotal:,.2f}', right_style),
            ])

        # Subtotal, descuento y total
        table_data.append(['', '', '', Paragraph('<b>Subtotal:</b>', right_style),
                            Paragraph(f'${cotizacion.subtotal_bruto:,.2f}', right_style)])
        if cotizacion.descuento_porcentaje > 0:
            table_data.append(['', '', '', Paragraph(f'<b>Desc. {cotizacion.descuento_porcentaje}%:</b>', right_style),
                                Paragraph(f'-${cotizacion.monto_descuento:,.2f}', right_style)])
        table_data.append(['', '', '', Paragraph('<b>TOTAL:</b>', right_style),
                            Paragraph(f'<b>${cotizacion.total:,.2f}</b>', right_style)])

        items_table = Table(table_data, colWidths=[2.2 * inch, 1.6 * inch, 0.7 * inch, 1.0 * inch, 1.1 * inch],
                            repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -(3 if cotizacion.descuento_porcentaje > 0 else 2)), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        elements.append(items_table)

    if cotizacion.observaciones:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph('<b>Observaciones:</b>', normal_style))
        elements.append(Paragraph(cotizacion.observaciones, normal_style))

    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        'ESTA COTIZACIÓN TIENE UNA VALIDEZ DE 7 DÍAS',
        ParagraphStyle('FooterNote', fontSize=8, alignment=TA_CENTER, textColor=colors.black)
    ))
    elements.append(Paragraph(
        'Paso a paso se llega lejos - GCSoft-2025',
        ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
    ))
    return elements


def generar_pdf_buffer(cotizacion):
    """Genera el PDF y devuelve el buffer en memoria (para email u otras uses)."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                             topMargin=60, bottomMargin=30)
    doc.build(_build_elements(cotizacion))
    buffer.seek(0)
    return buffer


def generar_pdf_cotizacion(cotizacion):
    """Genera respuesta HTTP con el PDF adjunto."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'
    buffer = generar_pdf_buffer(cotizacion)
    response.write(buffer.getvalue())
    return response
