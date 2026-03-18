from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.platypus.flowables import KeepTogether
from django.http import HttpResponse
from django.conf import settings
import os
from io import BytesIO
from decimal import Decimal

# ==============================
# PALETA CORPORATIVA GRIS ANTRACITA
# ==============================
COLOR_PRIMARY      = colors.HexColor('#212121')   # antracita oscuro
COLOR_SECONDARY    = colors.HexColor('#424242')   # antracita medio
COLOR_ACCENT       = colors.HexColor('#757575')   # gris medio
COLOR_HEADER_BG    = colors.HexColor('#212121')   # fondo header
COLOR_HEADER_TEXT  = colors.white
COLOR_ROW_ALT      = colors.HexColor('#F5F5F5')   # filas alternas
COLOR_ROW_HEADER   = colors.HexColor('#212121')   # fila encabezado tabla
COLOR_TOTAL_BG     = colors.HexColor('#EEEEEE')   # fila total
COLOR_BORDER       = colors.HexColor('#BDBDBD')   # bordes
COLOR_TEXT         = colors.HexColor('#212121')
COLOR_TEXT_MUTED   = colors.HexColor('#616161')
COLOR_FOOTER_LINE  = colors.HexColor('#424242')


def _styles():
    """Retorna diccionario de estilos tipográficos."""
    return {
        'empresa_nombre': ParagraphStyle(
            'EmpresaNombre',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=COLOR_HEADER_TEXT,
            leading=20,
        ),
        'empresa_sub': ParagraphStyle(
            'EmpresaSub',
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#C8E6C9'),
            leading=13,
            spaceAfter=2,
        ),
        'doc_titulo': ParagraphStyle(
            'DocTitulo',
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=COLOR_PRIMARY,
            alignment=TA_RIGHT,
            leading=26,
        ),
        'doc_numero': ParagraphStyle(
            'DocNumero',
            fontName='Helvetica',
            fontSize=10,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_RIGHT,
            leading=14,
        ),
        'seccion': ParagraphStyle(
            'Seccion',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=COLOR_ACCENT,
            leading=10,
            spaceBefore=14,
            spaceAfter=4,
            textTransform='uppercase',
        ),
        'campo_label': ParagraphStyle(
            'CampoLabel',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=COLOR_TEXT_MUTED,
            leading=12,
        ),
        'campo_valor': ParagraphStyle(
            'CampoValor',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=12,
        ),
        'tabla_header': ParagraphStyle(
            'TablaHeader',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=COLOR_HEADER_TEXT,
            leading=11,
        ),
        'tabla_celda': ParagraphStyle(
            'TablaCelda',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=11,
        ),
        'tabla_derecha': ParagraphStyle(
            'TablaDerecha',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=11,
            alignment=TA_RIGHT,
        ),
        'tabla_total': ParagraphStyle(
            'TablaTotal',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=COLOR_PRIMARY,
            leading=12,
            alignment=TA_RIGHT,
        ),
        'obs_titulo': ParagraphStyle(
            'ObsTitulo',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=COLOR_SECONDARY,
            leading=12,
            spaceBefore=12,
            spaceAfter=4,
        ),
        'obs_texto': ParagraphStyle(
            'ObsTexto',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=13,
        ),
        'footer_validez': ParagraphStyle(
            'FooterValidez',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=COLOR_PRIMARY,
            alignment=TA_CENTER,
            leading=11,
        ),
        'footer_slogan': ParagraphStyle(
            'FooterSlogan',
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
            leading=11,
        ),
        'footer_contacto': ParagraphStyle(
            'FooterContacto',
            fontName='Helvetica',
            fontSize=8,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER,
            leading=11,
        ),
    }


def _build_elements(cotizacion):
    st = _styles()
    elements = []

    # ── HEADER ────────────────────────────────────────────
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
         [Paragraph('Servicios Informáticos', st['empresa_sub'])],
         [Paragraph('Dilkendein 1278 &nbsp;|&nbsp; Tel: 358-4268768', st['empresa_sub'])]],
        colWidths=[3.5 * inch]
    )
    empresa_info.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    tipo_doc = cotizacion.tipo_documento.upper() if hasattr(cotizacion, 'tipo_documento') else 'COTIZACIÓN'
    doc_info = Table(
        [[Paragraph(tipo_doc, st['doc_titulo'])],
         [Paragraph(f'N° {cotizacion.numero}', st['doc_numero'])],
         [Paragraph(f'Fecha: {cotizacion.fecha.strftime("%d/%m/%Y")}', st['doc_numero'])]],
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

    # ── DATOS DEL CLIENTE ─────────────────────────────────
    elements.append(Paragraph('Datos del cliente', st['seccion']))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))

    cliente = cotizacion.cliente
    client_data = [
        [Paragraph('Nombre', st['campo_label']),
         Paragraph(cliente.nombre or '-', st['campo_valor']),
         Paragraph('Teléfono', st['campo_label']),
         Paragraph(cliente.telefono or '-', st['campo_valor'])],
        [Paragraph('Dirección', st['campo_label']),
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

    # ── TABLA DE PRODUCTOS ────────────────────────────────
    if cotizacion.items.exists():
        elements.append(Paragraph('Detalle de productos', st['seccion']))
        elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))

        table_data = [[
            Paragraph('Producto', st['tabla_header']),
            Paragraph('Proveedor', st['tabla_header']),
            Paragraph('Cant.', st['tabla_header']),
            Paragraph('Precio Unit.', st['tabla_header']),
            Paragraph('Subtotal', st['tabla_header']),
        ]]

        for i, item in enumerate(cotizacion.items.all()):
            row_bg = colors.white if i % 2 == 0 else COLOR_ROW_ALT
            table_data.append([
                Paragraph(item.producto.nombre, st['tabla_celda']),
                Paragraph(item.producto.proveedor.nombre, st['tabla_celda']),
                Paragraph(str(item.cantidad), st['tabla_celda']),
                Paragraph(f'${item.precio_unitario:,.2f}', st['tabla_derecha']),
                Paragraph(f'${item.subtotal:,.2f}', st['tabla_derecha']),
            ])

        # Filas de totales
        table_data.append(['', '', '', Paragraph('Subtotal:', st['tabla_derecha']),
                            Paragraph(f'${cotizacion.subtotal_bruto:,.2f}', st['tabla_derecha'])])
        if cotizacion.descuento_porcentaje > 0:
            table_data.append(['', '', '', Paragraph(f'Descuento {cotizacion.descuento_porcentaje}%:', st['tabla_derecha']),
                                Paragraph(f'-${cotizacion.monto_descuento:,.2f}', st['tabla_derecha'])])
        table_data.append(['', '', '', Paragraph('TOTAL:', st['tabla_total']),
                            Paragraph(f'${cotizacion.total:,.2f}', st['tabla_total'])])

        n_items = len(cotizacion.items.all())
        last_row = len(table_data) - 1
        subtotal_row = last_row - (2 if cotizacion.descuento_porcentaje > 0 else 1)

        items_table = Table(
            table_data,
            colWidths=[2.3*inch, 1.5*inch, 0.7*inch, 1.3*inch, 1.6*inch],
            repeatRows=1
        )
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_ROW_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
            ('TOPPADDING', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            # Filas alternas
            *[('BACKGROUND', (0, i), (-1, i), colors.white if (i % 2 == 1) else COLOR_ROW_ALT)
              for i in range(1, subtotal_row)],
            # Grid productos
            ('BOX', (0, 0), (-1, subtotal_row - 1), 0.5, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, subtotal_row - 1), 0.3, COLOR_BORDER),
            # Totales
            ('BACKGROUND', (3, subtotal_row), (-1, last_row), COLOR_TOTAL_BG),
            ('LINEABOVE', (3, subtotal_row), (-1, subtotal_row), 1, COLOR_SECONDARY),
            ('LINEBELOW', (3, last_row), (-1, last_row), 1.5, COLOR_PRIMARY),
            # General
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(items_table)

    # ── OBSERVACIONES ─────────────────────────────────────
    if cotizacion.observaciones:
        elements.append(Paragraph('Observaciones', st['obs_titulo']))
        obs_table = Table([[Paragraph(cotizacion.observaciones, st['obs_texto'])]],
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

    # ── FOOTER ────────────────────────────────────────────
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_FOOTER_LINE, spaceAfter=8))
    elements.append(Paragraph('Esta cotización tiene una validez de 7 días hábiles.', st['footer_validez']))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph('Paso a paso se llega lejos — GCSoft 2025', st['footer_slogan']))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph('GCinsumos &nbsp;|&nbsp; Dilkendein 1278, Río Cuarto &nbsp;|&nbsp; Tel: 358-4268768 &nbsp;|&nbsp; cristian.e.druetta@gmail.com', st['footer_contacto']))

    return elements


def generar_pdf_buffer(cotizacion):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=40, bottomMargin=30
    )
    doc.build(_build_elements(cotizacion))
    buffer.seek(0)
    return buffer


def generar_pdf_cotizacion(cotizacion):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'
    buffer = generar_pdf_buffer(cotizacion)
    response.write(buffer.getvalue())
    return response
