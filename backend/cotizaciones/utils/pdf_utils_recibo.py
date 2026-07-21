import os
from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, Image,
)
from reportlab.lib.utils import ImageReader

from cotizaciones.models import ConfiguracionAFIP

# Copied from pdf_utils.py palette
COLOR_PRIMARY      = colors.HexColor('#1C3A5E')
COLOR_SECONDARY    = colors.HexColor('#2E5D8E')
COLOR_ACCENT       = colors.HexColor('#4A7FB5')
COLOR_HEADER_BG    = colors.HexColor('#1C3A5E')
COLOR_HEADER_TEXT  = colors.white
COLOR_ROW_ALT      = colors.HexColor('#EEF3F9')
COLOR_ROW_HEADER   = colors.HexColor('#1C3A5E')
COLOR_TOTAL_BG     = colors.HexColor('#DDEAF5')
COLOR_BORDER       = colors.HexColor('#AACAE6')
COLOR_TEXT         = colors.HexColor('#1A1A2E')
COLOR_TEXT_MUTED   = colors.HexColor('#5A6A80')
COLOR_FOOTER_LINE  = colors.HexColor('#2E5D8E')


def _styles():
    return {
        'empresa_nombre': ParagraphStyle(
            'EmpresaNombre', fontName='Helvetica-Bold', fontSize=16,
            textColor=COLOR_HEADER_TEXT, leading=20,
        ),
        'empresa_sub': ParagraphStyle(
            'EmpresaSub', fontName='Helvetica', fontSize=9,
            textColor=colors.HexColor('#C8E6C9'), leading=13, spaceAfter=2,
        ),
        'doc_titulo': ParagraphStyle(
            'DocTitulo', fontName='Helvetica-Bold', fontSize=22,
            textColor=COLOR_HEADER_TEXT, alignment=TA_RIGHT, leading=26,
        ),
        'doc_numero_blanco': ParagraphStyle(
            'DocNumeroBlanco', fontName='Helvetica', fontSize=10,
            textColor=colors.white, alignment=TA_RIGHT, leading=14,
        ),
        'seccion': ParagraphStyle(
            'Seccion', fontName='Helvetica-Bold', fontSize=8,
            textColor=COLOR_SECONDARY, leading=10, spaceBefore=14, spaceAfter=4,
        ),
        'campo_label': ParagraphStyle(
            'CampoLabel', fontName='Helvetica-Bold', fontSize=9,
            textColor=COLOR_TEXT_MUTED, leading=12,
        ),
        'campo_valor': ParagraphStyle(
            'CampoValor', fontName='Helvetica', fontSize=9,
            textColor=COLOR_TEXT, leading=12,
        ),
        'tabla_header': ParagraphStyle(
            'TablaHeader', fontName='Helvetica-Bold', fontSize=9,
            textColor=COLOR_HEADER_TEXT, leading=11,
        ),
        'tabla_celda': ParagraphStyle(
            'TablaCelda', fontName='Helvetica', fontSize=9,
            textColor=COLOR_TEXT, leading=11,
        ),
        'tabla_derecha': ParagraphStyle(
            'TablaDerecha', fontName='Helvetica', fontSize=9,
            textColor=COLOR_TEXT, leading=11, alignment=TA_RIGHT,
        ),
        'tabla_total': ParagraphStyle(
            'TablaTotal', fontName='Helvetica-Bold', fontSize=10,
            textColor=COLOR_PRIMARY, leading=12, alignment=TA_RIGHT,
        ),
        'obs_titulo': ParagraphStyle(
            'ObsTitulo', fontName='Helvetica-Bold', fontSize=9,
            textColor=COLOR_SECONDARY, leading=12, spaceBefore=12, spaceAfter=4,
        ),
        'obs_texto': ParagraphStyle(
            'ObsTexto', fontName='Helvetica', fontSize=9,
            textColor=COLOR_TEXT, leading=13,
        ),
        'footer_slogan': ParagraphStyle(
            'FooterSlogan', fontName='Helvetica-Oblique', fontSize=8,
            textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=11,
        ),
        'footer_contacto': ParagraphStyle(
            'FooterContacto', fontName='Helvetica', fontSize=8,
            textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=11,
        ),
    }


def _build_elements(recibo):
    st = _styles()
    elements = []

    # â”€â”€ HEADER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        ir = ImageReader(logo_path)
        iw, ih = ir.getSize()
        logo_w = 1.2 * inch
        logo = Image(logo_path, width=logo_w, height=logo_w * (ih / iw))
    else:
        logo = Paragraph('', st['empresa_nombre'])

    empresa_info = Table(
        [[Paragraph('GCinsumos', st['empresa_nombre'])],
         [Paragraph('Servicios InformÃ¡ticos', st['empresa_sub'])],
         [Paragraph('Dilkendein 1278 &nbsp;|&nbsp; Tel: 358-4268768', st['empresa_sub'])]],
        colWidths=[3.5 * inch]
    )
    empresa_info.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    doc_info = Table(
        [[Paragraph('RECIBO', st['doc_titulo'])],
         [Paragraph(recibo.numero or '', st['doc_numero_blanco'])],
         [Paragraph(f'Fecha: {recibo.fecha.strftime("%d/%m/%Y")}', st['doc_numero_blanco'])]],
        colWidths=[2.5 * inch]
    )
    doc_info.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    header_inner = Table(
        [[logo, empresa_info, doc_info]],
        colWidths=[1.4 * inch, 3.5 * inch, 2.5 * inch]
    )
    header_inner.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    header_outer = Table([[header_inner]], colWidths=[7.4 * inch])
    header_outer.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_HEADER_BG),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_outer)
    elements.append(Spacer(1, 16))

    # â”€â”€ DATOS DEL CLIENTE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elements.append(Paragraph('Datos del cliente', st['seccion']))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))

    cliente = recibo.cliente
    client_data = [
        [Paragraph('Nombre', st['campo_label']),
         Paragraph(cliente.nombre or '-', st['campo_valor']),
         Paragraph('TelÃ©fono', st['campo_label']),
         Paragraph(cliente.telefono or '-', st['campo_valor'])],
        [Paragraph('DirecciÃ³n', st['campo_label']),
         Paragraph(cliente.direccion or 'No especificada', st['campo_valor']),
         Paragraph('Localidad', st['campo_label']),
         Paragraph(cliente.localidad or '-', st['campo_valor'])],
    ]
    client_table = Table(client_data, colWidths=[1.2*inch, 2.4*inch, 1.1*inch, 2.7*inch])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_ALT),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('LINEBELOW', (0, 0), (-1, 0), 0.3, COLOR_BORDER),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 14))

    # â”€â”€ TABLA DE PRODUCTOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    items = recibo.items.select_related('producto')
    if items.exists():
        elements.append(Paragraph('Detalle de productos', st['seccion']))
        elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))

        table_data = [[
            Paragraph('Producto', st['tabla_header']),
            Paragraph('Cant.', st['tabla_header']),
            Paragraph('Precio Unit.', st['tabla_header']),
            Paragraph('Subtotal', st['tabla_header']),
        ]]

        for i, item in enumerate(items):
            table_data.append([
                Paragraph(item.producto.nombre if item.producto else (item.descripcion or 'â€”'), st['tabla_celda']),
                Paragraph(str(item.cantidad), st['tabla_celda']),
                Paragraph(f'${item.precio_unitario:,.2f}', st['tabla_derecha']),
                Paragraph(f'${item.subtotal:,.2f}', st['tabla_derecha']),
            ])

        last_data_row = len(table_data)
        table_data.append(['', '', Paragraph('TOTAL:', st['tabla_total']),
                           Paragraph(f'${recibo.total:,.2f}', st['tabla_total'])])

        total_row = len(table_data) - 1
        items_table = Table(
            table_data,
            colWidths=[3.0*inch, 0.9*inch, 1.5*inch, 1.6*inch],
            repeatRows=1
        )
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_ROW_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
            ('TOPPADDING', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            *[('BACKGROUND', (0, i), (-1, i), colors.white if (i % 2 == 1) else COLOR_ROW_ALT)
              for i in range(1, last_data_row)],
            ('BOX', (0, 0), (-1, last_data_row - 1), 0.5, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, last_data_row - 1), 0.3, COLOR_BORDER),
            ('BACKGROUND', (2, last_data_row), (-1, total_row), COLOR_TOTAL_BG),
            ('LINEABOVE', (2, total_row), (-1, total_row), 1, COLOR_SECONDARY),
            ('LINEBELOW', (2, total_row), (-1, total_row), 1.5, COLOR_PRIMARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(items_table)

    # â”€â”€ FORMA DE PAGO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elements.append(Spacer(1, 8))
    pago_data = [[
        Paragraph('Forma de pago', st['campo_label']),
        Paragraph(dict(recibo.FORMA_PAGO_CHOICES).get(recibo.forma_pago, recibo.forma_pago), st['campo_valor']),
    ]]
    pago_table = Table(pago_data, colWidths=[1.5*inch, 5.9*inch])
    pago_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_ALT),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(pago_table)

    # â”€â”€ OBSERVACIONES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if recibo.observaciones:
        elements.append(Paragraph('Observaciones', st['obs_titulo']))
        obs_table = Table([[Paragraph(recibo.observaciones, st['obs_texto'])]],
                          colWidths=[7.4 * inch])
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_ALT),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(obs_table)

    # â”€â”€ FOOTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_FOOTER_LINE, spaceAfter=8))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph('Paso a paso se llega lejos â€” GCSoft 2025', st['footer_slogan']))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph('GCinsumos &nbsp;|&nbsp; Dilkendein 1278, RÃ­o Cuarto &nbsp;|&nbsp; Tel: 358-4268768 &nbsp;|&nbsp; cristian.e.druetta@gmail.com', st['footer_contacto']))

    return elements


def generar_pdf_recibo_buffer(recibo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    doc.build(_build_elements(recibo))
    buffer.seek(0)
    return buffer


def generar_pdf_recibo_response(recibo):
    response = HttpResponse(content_type='application/pdf')
    cliente_nombre = recibo.cliente.nombre if recibo.cliente and recibo.cliente.nombre else 'sin_nombre'
    cliente_slug = cliente_nombre.strip().replace(' ', '_')
    filename = f"Recibo_{recibo.numero}_{cliente_slug}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    buffer = generar_pdf_recibo_buffer(recibo)
    response.write(buffer.getvalue())
    return response
