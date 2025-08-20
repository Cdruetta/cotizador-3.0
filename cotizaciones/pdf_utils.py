from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.http import HttpResponse
from django.conf import settings
import os
from io import BytesIO

def generar_pdf_cotizacion(cotizacion):
    # Crear el objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'
    
    # Crear el documento PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    # Header de la empresa
    company_data = [
        [Paragraph('<b>SERVICIOS INFORMÁTICOS</b>', header_style)],
        [Paragraph('Dilkendein 1278 - Tel: 358-4268768', normal_style)],
        [Spacer(1, 12)]
    ]
    
    company_table = Table(company_data, colWidths=[6*inch])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 2, colors.darkblue),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 20))
    
    # Título del documento
    title = f"{cotizacion.get_tipo_documento_display().upper()} N° {cotizacion.numero}"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # Información del cliente
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
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(client_table)
    elements.append(Spacer(1, 20))
    
    # Tabla de productos
    if cotizacion.items.exists():
        # Headers de la tabla
        table_data = [['Producto', 'Proveedor', 'Cantidad', 'Precio Unit.', 'Total']]
        
        # Datos de los items
        for item in cotizacion.items.all():
            table_data.append([
                item.producto.nombre,
                item.producto.proveedor.nombre,
                str(item.cantidad),
                f'${item.precio_unitario:,.2f}',
                f'${item.subtotal:,.2f}'
            ])
        
        # Fila de total
        table_data.append(['', '', '', 'TOTAL:', f'${cotizacion.total:,.2f}'])
        
        # Crear la tabla
        items_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 0.8*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('ALIGN', (3, -1), (-1, -1), 'RIGHT'),
        ]))
        
        elements.append(items_table)
    
    # Observaciones
    if cotizacion.observaciones:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph('<b>Observaciones:</b>', normal_style))
        elements.append(Paragraph(cotizacion.observaciones, normal_style))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_text = "Paso a paso se llega lejos - GCSoft-2025 🏆🥇"
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y escribirlo a la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
