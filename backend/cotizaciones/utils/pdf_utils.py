from reportlab.lib.pagesizes import A4, landscape


from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse
from django.conf import settings
import os
from io import BytesIO
from decimal import Decimal
from xml.sax.saxutils import escape

from cotizaciones.models import ConfiguracionAFIP

# ==============================
# PALETA CORPORATIVA AZUL ACERO
# ==============================
COLOR_PRIMARY      = colors.HexColor('#1C3A5E')   # azul acero oscuro
COLOR_SECONDARY    = colors.HexColor('#2E5D8E')   # azul acero medio
COLOR_ACCENT       = colors.HexColor('#4A7FB5')   # azul acero claro
COLOR_HEADER_BG    = colors.HexColor('#1C3A5E')   # fondo header
COLOR_HEADER_TEXT  = colors.white
COLOR_ROW_ALT      = colors.HexColor('#EEF3F9')   # filas alternas
COLOR_ROW_HEADER   = colors.HexColor('#1C3A5E')   # fila encabezado tabla
COLOR_TOTAL_BG     = colors.HexColor('#DDEAF5')   # fila total
COLOR_BORDER       = colors.HexColor('#AACAE6')   # bordes
COLOR_TEXT         = colors.HexColor('#1A1A2E')
COLOR_TEXT_MUTED   = colors.HexColor('#5A6A80')
COLOR_FOOTER_LINE  = colors.HexColor('#2E5D8E')

# Factura: nombre y leyenda fiscal (colores = misma paleta que cotización arriba)
FACTURA_EMPRESA_NOMBRE = 'GCinsumos'
FACTURA_LEYENDA_MONOTRIBUTO = 'RESPONSABLE MONOTRIBUTO'


def _format_cuit_afip(raw):
    """Formatea CUIT con guiones si tiene 11 dígitos."""
    if not raw:
        return ''
    d = ''.join(c for c in str(raw) if c.isdigit())
    if len(d) != 11:
        return str(raw).strip()
    return f'{d[:2]}-{d[2:10]}-{d[10]}'


def _fmt_ar_num(val, decimales=2):
    """Número con coma decimal (estilo AR)."""
    if val is None:
        return ''
    q = Decimal(str(val)).quantize(Decimal(10) ** -decimales)
    s = format(q, 'f')
    if decimales == 0:
        return s.split('.')[0]
    ent, frac = s.split('.')
    return f'{ent},{frac}'


def _tipo_factura_afip(letra):
    """Letra AFIP → código numérico del comprobante."""
    return {'A': '01', 'B': '06', 'C': '11', 'M': '51'}.get((letra or 'C').upper(), '11')


def _styles_factura():
    """Estilos PDF factura — misma paleta corporativa que cotizaciones."""
    return {
        'razon_script': ParagraphStyle(
            'FacRazon',
            fontName='Times-Italic',
            fontSize=13,
            textColor=COLOR_TEXT,
            leading=15,
        ),
        'addr': ParagraphStyle(
            'FacAddr',
            fontName='Helvetica',
            fontSize=7,
            textColor=COLOR_TEXT,
            alignment=TA_RIGHT,
            leading=9,
        ),
        'factura_titulo': ParagraphStyle(
            'FacTitulo',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=COLOR_TEXT,
            alignment=TA_RIGHT,
            leading=18,
        ),
        'factura_meta': ParagraphStyle(
            'FacMeta',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            alignment=TA_RIGHT,
            leading=11,
        ),
        'factura_fiscal_small': ParagraphStyle(
            'FacFiscal',
            fontName='Helvetica',
            fontSize=7,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_RIGHT,
            leading=9,
        ),
        'iva_bar': ParagraphStyle(
            'FacIvaBar',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=COLOR_HEADER_TEXT,
            alignment=TA_CENTER,
            leading=12,
        ),
        'cliente_linea': ParagraphStyle(
            'FacCliente',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=11,
        ),
        'tab_head': ParagraphStyle(
            'FacTabHead',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=COLOR_HEADER_TEXT,
            alignment=TA_CENTER,
            leading=10,
        ),
        'tab_head_l': ParagraphStyle(
            'FacTabHeadL',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=COLOR_HEADER_TEXT,
            alignment=TA_LEFT,
            leading=10,
        ),
        'tab_cell': ParagraphStyle(
            'FacTabCell',
            fontName='Helvetica',
            fontSize=8,
            textColor=COLOR_TEXT,
            leading=10,
        ),
        'tab_cell_r': ParagraphStyle(
            'FacTabCellR',
            fontName='Helvetica',
            fontSize=8,
            textColor=COLOR_TEXT,
            alignment=TA_RIGHT,
            leading=10,
        ),
        'tab_cell_c': ParagraphStyle(
            'FacTabCellC',
            fontName='Helvetica',
            fontSize=8,
            textColor=COLOR_TEXT,
            alignment=TA_CENTER,
            leading=10,
        ),
        'cae_small': ParagraphStyle(
            'FacCae',
            fontName='Helvetica',
            fontSize=9,
            textColor=COLOR_TEXT,
            leading=11,
        ),
    }


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
            textColor=COLOR_SECONDARY,
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


# ==============================
# FACTURA PDF (layout comprobante AR)
# ==============================

def _factura_logo_path():
    for name in ('logo_factura.png', 'logo.png'):
        p = os.path.join(settings.BASE_DIR, 'static', 'images', name)
        if os.path.exists(p):
            return p
    return None


def _build_elements_factura(factura):
    """PDF factura horizontal: cabecera GCinsumos, barra monotributo, tabla ítems tipo comprobante AR."""
    st = _styles_factura()
    sf = _styles()
    elements = []
    config = ConfiguracionAFIP.get_config()
    nombre_marca = FACTURA_EMPRESA_NOMBRE
    domicilio_emitter = (config.domicilio if config else '') or ''
    cuit_emitter = _format_cuit_afip(config.cuit) if config else ''

    # ── Logo + marca izquierda ─────────────────────────────
    logo_path = _factura_logo_path()
    left_stack = []
    if logo_path:
        ir = ImageReader(logo_path)
        iw, ih = ir.getSize()
        logo_w = 1.15 * inch
        left_stack.append(Image(logo_path, width=logo_w, height=logo_w * (ih / iw)))
    left_stack.append(Paragraph(escape(nombre_marca), st['razon_script']))
    col_left = Table([[c] for c in left_stack], colWidths=[2.15 * inch])
    col_left.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    # ── Centro: domicilio fiscal + recuadro letra/código ───
    addr_chunks = []
    for chunk in domicilio_emitter.replace('|', '\n').splitlines():
        chunk = chunk.strip()
        if chunk:
            addr_chunks.append(chunk)
    if not addr_chunks:
        addr_chunks = [' ']
    addr_html = '<br/>'.join(escape(c) for c in addr_chunks)
    addr_block = Paragraph(addr_html, st['addr'])

    letra = (factura.tipo or 'C').upper()
    cod_afip = _tipo_factura_afip(letra)
    letra_style = ParagraphStyle(
        'FacLetra', fontName='Helvetica-Bold', fontSize=26, textColor=COLOR_HEADER_TEXT,
        alignment=TA_CENTER, leading=28,
    )
    letter_box = Table(
        [[Paragraph(letra, letra_style)]],
        colWidths=[0.52 * inch],
        rowHeights=[0.52 * inch],
    )
    letter_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_HEADER),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    codigo_par = Paragraph(f'CODIGO {cod_afip}', ParagraphStyle(
        'FacCod', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT,
        alignment=TA_CENTER, leading=9,
    ))
    col_mid_inner = Table(
        [[addr_block],
         [Spacer(1, 6)],
         [letter_box],
         [codigo_par]],
        colWidths=[3.95 * inch],
    )
    col_mid_inner.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    col_mid = Table([[col_mid_inner]], colWidths=[4.05 * inch])

    # ── Derecha: tipo comprobante + datos ─────────────────
    punto_venta = factura.punto_venta or 0
    numero = factura.numero or 0
    titulo_doc = ParagraphStyle(
        'FacFacturaTit', fontName='Helvetica-Bold', fontSize=18,
        textColor=COLOR_PRIMARY, alignment=TA_RIGHT, leading=20,
    )
    pv_num = f'Nº : {punto_venta:04d}-{numero:08d}'
    fecha_txt = f'Fecha: {factura.fecha.strftime("%d/%m/%Y")}'
    fiscal_extra = []
    if cuit_emitter:
        fiscal_extra.append(f'C.U.I.T.: {cuit_emitter}')
    fiscal_extra.append('INGRESOS BRUTOS — | ESTABLEC.: — | INICIO ACT.: —')
    fiscal_html = '<br/>'.join(escape(x) for x in fiscal_extra)
    col_right = Table([
        [Paragraph('FACTURA', titulo_doc)],
        [Paragraph(pv_num, st['factura_meta'])],
        [Paragraph(fecha_txt, st['factura_meta'])],
        [Spacer(1, 6)],
        [Paragraph(fiscal_html, st['factura_fiscal_small'])],
    ], colWidths=[3.35 * inch])
    col_right.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    header_row = Table([[col_left, col_mid, col_right]], colWidths=[2.15 * inch, 4.05 * inch, 3.35 * inch])
    header_row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    elements.append(header_row)

    # ── Barra situación fiscal (monotributo) ──────────────
    iva_bar = Table(
        [[Paragraph(FACTURA_LEYENDA_MONOTRIBUTO, st['iva_bar'])]],
        colWidths=[9.55 * inch],
    )
    iva_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_HEADER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(Spacer(1, 2))
    elements.append(iva_bar)
    elements.append(Spacer(1, 10))

    # ── Cliente ───────────────────────────────────────────
    cliente = factura.cliente
    nombre_c = cliente.nombre or '—'
    prov = getattr(cliente, 'provincia', None) or '—'
    dom = (cliente.direccion or '').replace('\n', ' ').strip() or '—'
    loc = cliente.localidad or '—'
    cond_iva_receptor = 'CONSUMIDOR FINAL' if letra == 'C' else '—'
    cuit_cli = getattr(cliente, 'cuit', None)
    cuit_cli_txt = _format_cuit_afip(cuit_cli) if cuit_cli else '—'

    cell = st['cliente_linea']
    cli_tbl = Table([
        [
            Paragraph(f'<b>Señores</b> : {escape(nombre_c)}', cell),
            Paragraph(f'<b>Provincia</b> : {escape(str(prov))}', cell),
            Paragraph('&nbsp;', cell),
        ],
        [
            Paragraph(f'<b>Domicilio</b> : {escape(dom)}', cell),
            Paragraph(f'<b>Localidad</b> : {escape(loc)}', cell),
            Paragraph('&nbsp;', cell),
        ],
        [
            Paragraph(f'<b>IVA</b> : {escape(cond_iva_receptor)}', cell),
            Paragraph(f'<b>CUIT</b> : {escape(cuit_cli_txt)}', cell),
            Paragraph('<b>O.C.</b> : ', cell),
        ],
        [
            Paragraph('<b>Condición Venta</b> : Contado', cell),
            Paragraph('<b>Remito</b> : —', cell),
            Paragraph('&nbsp;', cell),
        ],
    ], colWidths=[3.45 * inch, 3.45 * inch, 2.65 * inch])
    cli_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, COLOR_BORDER),
    ]))
    elements.append(cli_tbl)
    elements.append(Spacer(1, 12))

    # ── Ítems ─────────────────────────────────────────────
    items = list(factura.items.all())
    head = st['tab_head']
    head_l = st['tab_head_l']
    tc = st['tab_cell']
    tcr = st['tab_cell_r']
    tcc = st['tab_cell_c']

    table_data = [[
        Paragraph('CODIGO', head_l),
        Paragraph('CANT', head),
        Paragraph('DETALLE / DESCRIPCION ADICIONAL', head_l),
        Paragraph('IVA', head),
        Paragraph('P. Unitario', head),
        Paragraph('Bonif', head),
        Paragraph('P. TOTAL', head),
    ]]

    for item in items:
        cant = item.cantidad
        cant_dec = 0 if (cant % 1 == 0) else 2
        cant_txt = _fmt_ar_num(cant, cant_dec)
        pu_txt = _fmt_ar_num(item.precio_unit, 4)
        # IVA en Factura C no discriminado — columna alineada al formato modelo
        iva_txt = '0 %' if letra == 'C' else '—'
        table_data.append([
            Paragraph('—', tc),
            Paragraph(cant_txt, tcc),
            Paragraph(escape(item.descripcion), tc),
            Paragraph(iva_txt, tcc),
            Paragraph(pu_txt, tcr),
            Paragraph('0,0 %', tcr),
            Paragraph(_fmt_ar_num(item.subtotal, 2), tcr),
        ])

    subtotal = factura.neto or Decimal('0')
    total = factura.total or Decimal('0')
    total_style = ParagraphStyle(
        'FacTot', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_PRIMARY, alignment=TA_RIGHT,
    )
    table_data.append([
        '', '', '', '', '',
        Paragraph('<b>TOTAL</b>', total_style),
        Paragraph(f'<b>{_fmt_ar_num(total, 2)}</b>', total_style),
    ])

    last_row = len(table_data) - 1
    data_rows = last_row

    cw = [0.9 * inch, 0.5 * inch, 5.3 * inch, 0.5 * inch, 0.9 * inch, 0.55 * inch, 0.9 * inch]
    items_table = Table(table_data, colWidths=cw, repeatRows=1)

    body_bg = []
    for i in range(1, data_rows):
        bg = colors.white if i % 2 else COLOR_ROW_ALT
        body_bg.append(('BACKGROUND', (0, i), (-1, i), bg))

    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_ROW_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_HEADER_TEXT),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        *body_bg,
        ('BOX', (0, 0), (-1, data_rows), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, data_rows), 0.25, COLOR_BORDER),
        ('LINEABOVE', (0, last_row), (-1, last_row), 1, COLOR_SECONDARY),
        ('BACKGROUND', (0, last_row), (-1, last_row), COLOR_TOTAL_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    items_table.setStyle(TableStyle(ts))
    elements.append(items_table)

    elements.append(Spacer(1, 8))
    neto_line = Paragraph(
        f'Importe neto gravado: {_fmt_ar_num(subtotal, 2)} &nbsp;&nbsp; Total factura: {_fmt_ar_num(total, 2)}',
        st['cae_small'],
    )
    elements.append(neto_line)

    # ── CAE ───────────────────────────────────────────────
    if factura.estado == 'autorizada' and factura.cae:
        elements.append(Spacer(1, 10))
        vto = factura.cae_vencimiento.strftime('%d/%m/%Y') if factura.cae_vencimiento else '—'
        cae_txt = f'CAE Nº {factura.cae} — Fecha de vencimiento CAE: {vto}'
        elements.append(Paragraph(cae_txt, st['cae_small']))
    else:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph('<i>Borrador — pendiente de autorización ARCA</i>', st['cae_small']))

    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))
    pie = escape(nombre_marca)
    if config and config.domicilio:
        pie += f' — {escape(config.domicilio)}'
    elements.append(Paragraph(pie, sf['footer_contacto']))

    return elements


def _factura_watermark_and_frame(canvas, doc):
    """Marca de agua centrada (logo) + marco alrededor de toda la hoja."""
    # --- Marco (bordes) ---
    canvas.saveState()
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(1)

    # Rectángulo respetando márgenes del documento
    x = doc.leftMargin
    y = doc.bottomMargin
    w = doc.width
    h = doc.height
    canvas.rect(x, y, w, h, stroke=1, fill=0)

    # --- Marca de agua (logo) ---
    logo_path = _factura_logo_path()
    if logo_path:
        try:
            ir = ImageReader(logo_path)
            iw, ih = ir.getSize()

            # Tamaño grande centrado (horizontal)
            # En landscape A4 el área útil es más ancha; ajustamos un poco.
            target_w = min(w * 0.75, 6.0 * inch)
            target_h = target_w * (ih / iw) if iw else target_w

            # Ubicación: centrada en X y más abajo en Y (marca de agua “al fondo”)
            cx = x + w / 2
            cy = y + h / 2 - (0.18 * h)
            img_x = cx - target_w / 2
            img_y = cy - target_h / 2


            # Transparencia para que no tape el contenido
            if hasattr(canvas, 'setFillAlpha'):
                canvas.setFillAlpha(0.12)

            canvas.drawImage(logo_path, img_x, img_y, width=target_w, height=target_h, mask='auto')
        except Exception:
            # Si algo falla con el logo, no rompas el PDF
            pass

    canvas.restoreState()


def generar_pdf_factura_buffer(factura):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),

        rightMargin=28, leftMargin=28,
        topMargin=36, bottomMargin=32,
    )

    elements = _build_elements_factura(factura)
    doc.build(
        elements,
        onFirstPage=_factura_watermark_and_frame,
        onLaterPages=_factura_watermark_and_frame,
    )
    buffer.seek(0)
    return buffer



def generar_pdf_factura(factura):
    response = HttpResponse(content_type='application/pdf')
    pv = factura.punto_venta or 0
    numero = factura.numero or 0
    response['Content-Disposition'] = f'attachment; filename="factura_{pv:04d}-{numero:08d}.pdf"'
    buffer = generar_pdf_factura_buffer(factura)
    response.write(buffer.getvalue())
    return response


