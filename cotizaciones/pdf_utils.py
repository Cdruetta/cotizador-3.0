from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader  # Agregado para leer dimensiones reales del logo
from django.http import HttpResponse
from django.conf import settings
import os
from io import BytesIO

def generar_pdf_cotizacion(cotizacion):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=30)

    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle('Title', fontSize=18, alignment=TA_CENTER, textColor=colors.darkblue, spaceAfter=20)
    normal_style = ParagraphStyle('Normal', fontSize=10, leading=12, spaceAfter=6)
    header_style = ParagraphStyle('Header', fontSize=12, alignment=TA_CENTER, textColor=colors.darkblue)
    table_cell_style = ParagraphStyle('TableCell', fontSize=9, leading=11)

    # Preparar logo para la tabla (mantener proporciones reales)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    logo_img = None
    if os.path.exists(logo_path):
        img_reader = ImageReader(logo_path)
        img_width, img_height = img_reader.getSize()
        desired_width = 1.4 * inch
        aspect_ratio = img_height / img_width
        logo_img = Image(logo_path, width=desired_width, height=desired_width * aspect_ratio)
        logo_img.hAlign = 'CENTER'

    # Tabla con logo y texto
    company_info = [
        [
            logo_img if logo_img else '',
            Paragraph('<font size=12><b>GCinsumos</b></font><br/><b>SERVICIOS INFORMÁTICOS</b><br/><font size=10>Dilkendein 1278 - Tel: 358-4268768</font>', normal_style)
        ],
    ]
    company_table = Table(company_info, colWidths=[1.7*inch, 4.3*inch])
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('BOX', (0, 0), (-1, -1), 1, colors.darkblue),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
        ('LEFTPADDING', (0, 0), (0, 0), 6),
        ('RIGHTPADDING', (0, 0), (0, 0), 6),
        ('TOPPADDING', (0, 0), (0, 0), 6),
        ('BOTTOMPADDING', (0, 0), (0, 0), 6),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 20))

    # Título del documento
    title = f"{cotizacion.get_tipo_documento_display().upper()} N° {cotizacion.numero}"
    elements.append(Paragraph(title, title_style))

    # Datos del cliente
    client_data = [
        ['Cliente:', cotizacion.cliente.nombre],
        ['Dirección:', cotizacion.cliente.direccion or 'No especificada'],
        ['Teléfono:', cotizacion.cliente.telefono or '-'],
        ['Localidad:', cotizacion.cliente.localidad or '-'],
        ['Fecha:', cotizacion.fecha.strftime('%d/%m/%Y')],
    ]
    client_table = Table(client_data, colWidths=[1.5*inch, 4.5*inch])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
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
            Paragraph('<b>Cantidad</b>', table_cell_style),
            Paragraph('<b>Precio Unit.</b>', table_cell_style),
            Paragraph('<b>Total</b>', table_cell_style),
        ]]

        for item in cotizacion.items.all():
            table_data.append([
                Paragraph(item.producto.nombre, table_cell_style),
                Paragraph(item.producto.proveedor.nombre, table_cell_style),
                Paragraph(str(item.cantidad), table_cell_style),
                Paragraph(f"${item.precio_unitario:,.2f}", table_cell_style),
                Paragraph(f"${item.subtotal:,.2f}", table_cell_style),
            ])

        # Total
        table_data.append(['', '', '', Paragraph('<b>TOTAL:</b>', table_cell_style), Paragraph(f"${cotizacion.total:,.2f}", table_cell_style)])

        col_widths = [2.2*inch, 1.6*inch, 0.8*inch, 1*inch, 1*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (2, 1), (-1, -2), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (3, -1), (3, -1), 'RIGHT'),
            ('ALIGN', (4, -1), (4, -1), 'RIGHT'),
        ]))
        elements.append(items_table)

    # Observaciones
    if cotizacion.observaciones:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph('<b>Observaciones:</b>', normal_style))
        elements.append(Paragraph(cotizacion.observaciones, normal_style))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
    "ESTA COTIZACIÓN TIENE UNA VALIDEZ DE 7 DÍAS",
    ParagraphStyle('FooterNote', fontSize=8, alignment=TA_CENTER, textColor=colors.black)
))
    elements.append(Paragraph(
        "Paso a paso se llega lejos - GCSoft-2025 🏆🥇",
        ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
    ))

    # Generar PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
