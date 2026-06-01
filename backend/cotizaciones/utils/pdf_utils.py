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
import json
import base64
from io import BytesIO
from decimal import Decimal
from xml.sax.saxutils import escape
import qrcode

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
            textColor=COLOR_HEADER_TEXT,
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
        'doc_numero_blanco': ParagraphStyle(
            'DocNumeroBlanco',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.white,
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
         [Paragraph(cotizacion.numero or '', st['doc_numero_blanco'])],
         [Paragraph(f'Fecha: {cotizacion.fecha.strftime("%d/%m/%Y")}', st['doc_numero_blanco'])]],
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
    validez_texto = (
        'Esta cotización tiene una validez de 7 días hábiles.'
        if getattr(cotizacion, 'tipo_documento', '') != 'recibo'
        else None
    )
    if validez_texto:
        elements.append(Paragraph(validez_texto, st['footer_validez']))

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


def _factura_logo_path():
    for name in ('logo_factura.png', 'logo.png'):
        p = os.path.join(settings.BASE_DIR, 'static', 'images', name)
        if os.path.exists(p):
            return p
    return None


def _factura_qr_image(factura):
    """Genera imagen QR compatible AFIP/ARCA."""
    config = ConfiguracionAFIP.get_config()
    if not config or not config.cuit:
        return None
    cuit = config.cuit.replace('-', '').replace(' ', '')
    cuit_int = int(cuit)
    letra = (factura.tipo or 'C').upper()
    cod_afip = _tipo_factura_afip(letra)
    doc_tipo = 99
    doc_nro = 0
    if factura.cliente:
        cuit_cli = getattr(factura.cliente, 'cuit', None)
        if cuit_cli:
            doc_tipo = 80
            doc_nro = int(cuit_cli.replace('-', '').replace(' ', ''))
    payload = {
        'ver': 1,
        'fecha': factura.fecha.strftime('%Y-%m-%d'),
        'cuit': cuit_int,
        'ptoVta': factura.punto_venta or 0,
        'tipoCmp': cod_afip,
        'nroCmp': factura.numero or 0,
        'importe': float(factura.total or 0),
        'moneda': 'PES',
        'ctz': 1,
        'tipoDocRec': doc_tipo,
        'nroDocRec': doc_nro,
        'tipoCodAut': 'E',
        'codAut': int(factura.cae) if factura.cae else 0,
    }
    json_str = json.dumps(payload, separators=(',', ':'))
    b64 = base64.urlsafe_b64encode(json_str.encode()).rstrip(b'=').decode()
    url = f'https://www.afip.gob.ar/fe/qr/?p={b64}'
    img = qrcode.make(url, box_size=4, border=1)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def _build_elements_factura(factura):
    """PDF factura vertical estilo AFIP profesional."""
    elements = []
    config = ConfiguracionAFIP.get_config()
    razon_social = (config.razon_social if config else '') or FACTURA_EMPRESA_NOMBRE
    cuit_emitter = _format_cuit_afip(config.cuit) if config else ''
    domicilio_emitter = (config.domicilio if config else '') or ''
    letra = (factura.tipo or 'C').upper()
    pw = 6.5 * inch

    # ── Estilos ───────────────────────────────────────────
    s_emp = ParagraphStyle('FE', fontName='Helvetica-Bold', fontSize=13, textColor=COLOR_PRIMARY, leading=16)
    s_info = ParagraphStyle('FI', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_info_bold = ParagraphStyle('FIB', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_info_muted = ParagraphStyle('FIM', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT_MUTED, leading=10)
    s_factura_tit = ParagraphStyle('FFT', fontName='Helvetica-Bold', fontSize=18, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=22)
    s_factura_meta = ParagraphStyle('FFM', fontName='Helvetica', fontSize=8, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=10)
    s_factura_meta_b = ParagraphStyle('FFMB', fontName='Helvetica-Bold', fontSize=11, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=14)
    s_cli_tit = ParagraphStyle('FCT', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_PRIMARY, leading=12)
    s_cli_val = ParagraphStyle('FCV', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, leading=12)
    s_cli_val_b = ParagraphStyle('FCVB', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_TEXT, leading=12)
    s_th = ParagraphStyle('FTH', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=10)
    s_th_l = ParagraphStyle('FTHL', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_HEADER_TEXT, leading=10)
    s_td = ParagraphStyle('FTD', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_tdr = ParagraphStyle('FTDR', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=10)
    s_tdc = ParagraphStyle('FTDC', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, alignment=TA_CENTER, leading=10)
    s_tot_lbl = ParagraphStyle('FTL', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=13)
    s_tot_val = ParagraphStyle('FTV', fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_PRIMARY, alignment=TA_RIGHT, leading=17)
    s_sub_lbl = ParagraphStyle('FSL', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=11)
    s_sub_val = ParagraphStyle('FSV', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=11)
    s_cae = ParagraphStyle('FCAE', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, alignment=TA_CENTER, leading=10)
    s_arca = ParagraphStyle('FARCA', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=9)
    s_footer = ParagraphStyle('FPT', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=9)

    # ══════════════════════════════════════════════════════
    # ENCABEZADO: dos columnas
    # ══════════════════════════════════════════════════════
    # ── Columna izquierda: logo + datos del emisor ───────
    left_cells = []
    logo_path = _factura_logo_path()
    if logo_path:
        ir = ImageReader(logo_path)
        iw, ih = ir.getSize()
        logo_w = 0.95 * inch
        left_cells.append(Image(logo_path, width=logo_w, height=logo_w * (ih / iw)))
        left_cells.append(Spacer(1, 4))

    left_cells.append(Paragraph(escape(razon_social), s_emp))
    left_cells.append(Spacer(1, 2))

    emit_lines = []
    if config and config.razon_social:
        emit_lines.append(f'<b>Razón Social:</b> {escape(config.razon_social)}')
    if cuit_emitter:
        emit_lines.append(f'<b>CUIT:</b> {escape(cuit_emitter)}')
    emit_lines.append('<b>Condición IVA:</b> Monotributista')
    if domicilio_emitter:
        emit_lines.append(f'<b>Domicilio:</b> {escape(domicilio_emitter)}')
    left_cells.append(Paragraph('<br/>'.join(emit_lines), s_info))

    col_left = Table([[c] for c in left_cells], colWidths=[3.5 * inch])
    col_left.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # ── Columna derecha: recuadro FACTURA ─────────────────
    pv = factura.punto_venta or 0
    num = factura.numero or 0
    fecha_txt = factura.fecha.strftime('%d/%m/%Y')
    right_inner = Table([
        [Paragraph('FACTURA', s_factura_tit)],
        [Paragraph(letra, ParagraphStyle('FFL', fontName='Helvetica-Bold', fontSize=32, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=36))],
        [Spacer(1, 6)],
        [Paragraph(f'Punto de Venta<br/><b>{pv:04d}</b>', s_factura_meta)],
        [Spacer(1, 3)],
        [Paragraph(f'Comp. N°<br/><b>{num:08d}</b>', s_factura_meta)],
        [Spacer(1, 3)],
        [Paragraph(f'Fecha<br/><b>{fecha_txt}</b>', s_factura_meta)],
    ], colWidths=[2.35 * inch])
    right_inner.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    col_right = Table([[right_inner]], colWidths=[2.65 * inch])
    col_right.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    header_tbl = Table([[col_left, col_right]], colWidths=[3.75 * inch, 2.75 * inch])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_tbl)

    # ══════════════════════════════════════════════════════
    # BARRA MONOTRIBUTO
    # ══════════════════════════════════════════════════════
    elements.append(Spacer(1, 8))
    iva_bar = Table(
        [[Paragraph(FACTURA_LEYENDA_MONOTRIBUTO, ParagraphStyle(
            'FIvaB', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_HEADER_TEXT,
            alignment=TA_CENTER, leading=11,
        ))]],
        colWidths=[pw],
    )
    iva_bar.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_HEADER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(iva_bar)
    elements.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════
    # CLIENTE — con borde y fondo suave
    # ══════════════════════════════════════════════════════
    cliente = factura.cliente
    nombre_c = cliente.nombre or '—'
    dom_c = (cliente.direccion or '').replace('\n', ' ').strip() or '—'
    loc_c = cliente.localidad or '—'
    prov_c = getattr(cliente, 'provincia', None) or '—'
    cuit_cli = getattr(cliente, 'cuit', None)
    cuit_cli_txt = _format_cuit_afip(cuit_cli) if cuit_cli else '—'
    if cuit_cli:
        cond_iva_receptor = 'RESPONSABLE MONOTRIBUTO'
    else:
        cond_iva_receptor = 'CONSUMIDOR FINAL'

    cli_inner = Table([
        [Paragraph('DATOS DEL CLIENTE', s_cli_tit)],
        [Spacer(1, 3)],
        [Paragraph(f'<b>Nombre/Razón Social:</b>  {escape(nombre_c)}', s_cli_val)],
        [Paragraph(f'<b>CUIT/DNI:</b>  {escape(cuit_cli_txt)}&nbsp;&nbsp;&nbsp;&nbsp;<b>Condición IVA:</b>  {escape(cond_iva_receptor)}', s_cli_val)],
        [Paragraph(f'<b>Domicilio:</b>  {escape(dom_c)}, {escape(loc_c)}, {escape(prov_c)}', s_cli_val)],
    ], colWidths=[pw - 0.2 * inch])
    cli_inner.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    cli_tbl = Table([[cli_inner]], colWidths=[pw])
    cli_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_ROW_ALT),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cli_tbl)
    elements.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════
    # TABLA DE DETALLE
    # ══════════════════════════════════════════════════════
    items = list(factura.items.all())
    cw_items = [0.55 * inch, pw - 1.9 * inch, 0.85 * inch, 0.85 * inch]
    table_data = [[
        Paragraph('Cant.', s_th),
        Paragraph('Descripción', s_th_l),
        Paragraph('P. Unit.', s_th),
        Paragraph('Subtotal', s_th),
    ]]
    for item in items:
        cant = item.cantidad
        cant_dec = 0 if (cant % 1 == 0) else 2
        cant_txt = _fmt_ar_num(cant, cant_dec)
        pu_txt = _fmt_ar_num(item.precio_unit, 2)
        table_data.append([
            Paragraph(cant_txt, s_tdc),
            Paragraph(escape(item.descripcion), s_td),
            Paragraph(f'${pu_txt}', s_tdr),
            Paragraph(f'${_fmt_ar_num(item.subtotal, 2)}', s_tdr),
        ])

    total = factura.total or Decimal('0')
    neto = factura.neto or Decimal('0')
    descuento = neto - total if neto > total else Decimal('0')

    # Add subtotal/descuento/total rows
    data_rows = len(table_data)
    table_data.append([
        Paragraph('', s_td), Paragraph('', s_td),
        Paragraph('SUBTOTAL', s_sub_lbl),
        Paragraph(f'${_fmt_ar_num(neto, 2)}', s_sub_val),
    ])
    table_data.append([
        Paragraph('', s_td), Paragraph('', s_td),
        Paragraph('DESCUENTO', s_sub_lbl),
        Paragraph(f'${_fmt_ar_num(descuento, 2)}', s_sub_val),
    ])
    table_data.append([
        Paragraph('', s_td), Paragraph('', s_td),
        Paragraph('TOTAL', s_tot_lbl),
        Paragraph(f'${_fmt_ar_num(total, 2)}', s_tot_val),
    ])

    last_row = len(table_data) - 1
    items_table = Table(table_data, colWidths=cw_items, repeatRows=1)

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
        ('BOX', (0, 0), (-1, last_row), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, data_rows - 1), 0.25, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, data_rows - 1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, data_rows - 1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        # Total row highlight
        ('LINEABOVE', (0, last_row), (-1, last_row), 1.5, COLOR_SECONDARY),
        ('BACKGROUND', (0, last_row), (-1, last_row), COLOR_TOTAL_BG),
        ('TOPPADDING', (0, last_row), (-1, last_row), 6),
        ('BOTTOMPADDING', (0, last_row), (-1, last_row), 6),
    ]
    items_table.setStyle(TableStyle(ts))
    elements.append(items_table)

    # ══════════════════════════════════════════════════════
    # MONEDA + ADVERTENCIA $10M
    # ══════════════════════════════════════════════════════
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Moneda: PESOS ($) — Todos los importes están expresados en Pesos Argentinos', s_cae))
    if not cuit_cli and total >= Decimal('10000000'):
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(
            '<i>Importe >= $10.000.000 — obligatorio informar DNI/CUIT/CUIL/CDI del comprador</i>',
            s_cae,
        ))

    # ══════════════════════════════════════════════════════
    # CAE + QR + PIE
    # ══════════════════════════════════════════════════════
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=6))

    if factura.estado == 'autorizada' and factura.cae:
        vto = factura.cae_vencimiento.strftime('%d/%m/%Y') if factura.cae_vencimiento else '—'
        # QR + CAE side by side
        qr_buf = _factura_qr_image(factura)
        if qr_buf:
            qr_img = Image(qr_buf, width=0.7 * inch, height=0.7 * inch)
            cae_block = [
                [Paragraph(f'CAE: <b>{factura.cae}</b>', s_cae)],
                [Paragraph(f'Vto. CAE: <b>{vto}</b>', s_cae)],
                [Spacer(1, 4)],
                [Paragraph('Comprobante autorizado por ARCA (ex AFIP)', s_arca)],
            ]
            if domicilio_emitter:
                cae_block.append([Spacer(1, 2)])
                cae_block.append([Paragraph(escape(domicilio_emitter), s_arca)])

            cae_tbl = Table(cae_block, colWidths=[pw - 1.0 * inch])
            cae_tbl.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            footer_row = Table([[qr_img, cae_tbl]], colWidths=[0.9 * inch, pw - 0.9 * inch])
            footer_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(footer_row)
        else:
            elements.append(Paragraph(f'CAE: <b>{factura.cae}</b>', s_cae))
            elements.append(Paragraph(f'Vto. CAE: <b>{vto}</b>', s_cae))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph('Comprobante autorizado por ARCA (ex AFIP)', s_arca))
    else:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph('<i>Borrador — pendiente de autorización ARCA</i>', s_cae))

    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=4))
    pie = escape(razon_social)
    if config and config.domicilio:
        pie += f' — {escape(config.domicilio)}'
    elements.append(Paragraph(pie, s_footer))

    return elements


def _factura_watermark_and_frame(canvas, doc):
    """Marca de agua centrada (logo) + marco alrededor de toda la hoja."""
    canvas.saveState()
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(1)

    x = doc.leftMargin
    y = doc.bottomMargin
    w = doc.width
    h = doc.height
    canvas.rect(x, y, w, h, stroke=1, fill=0)

    logo_path = _factura_logo_path()
    if logo_path:
        try:
            ir = ImageReader(logo_path)
            iw, ih = ir.getSize()

            target_w = min(w * 0.75, 6.0 * inch)
            target_h = target_w * (ih / iw) if iw else target_w

            cx = x + w / 2
            cy = y + h / 2
            img_x = cx - target_w / 2
            img_y = cy - target_h / 2

            if hasattr(canvas, 'setFillAlpha'):
                canvas.setFillAlpha(0.12)

            canvas.drawImage(logo_path, img_x, img_y, width=target_w, height=target_h, mask='auto')
        except Exception:
            pass

    canvas.restoreState()


def generar_pdf_factura_buffer(factura):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
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


# ==========================================
# FUNCIONES DE DESCARGA CON NOMBRE DINÁMICO
# ==========================================

def generar_pdf_cotizacion(cotizacion):
    response = HttpResponse(content_type='application/pdf')
    
    # 1. Extraemos y limpiamos el nombre del cliente
    cliente_nombre = cotizacion.cliente.nombre if cotizacion.cliente and cotizacion.cliente.nombre else 'sin_nombre'
    cliente_slug = cliente_nombre.strip().replace(' ', '_')
    
    # 2. Limpiamos el número del documento base (sacamos el '°' y espacios)
    num_doc_raw = (cotizacion.numero or '').replace('°', '').strip()
    
    # 3. Detectamos el tipo de documento (por atributo o por texto en el número)
    tipo_doc_attr = getattr(cotizacion, 'tipo_documento', '').lower()
    
    if 'recibo' in tipo_doc_attr or 'recibo' in num_doc_raw.lower():
        # Limpiamos posibles redundancias de la palabra "Recibo"
        clean_num = num_doc_raw.replace('Recibo_', '').replace('recibo_', '').replace('Recibo', '').replace('recibo', '').strip('_ ')
        filename = f"Recibo_{clean_num}_{cliente_slug}.pdf"
        
    elif 'cotizacion' in tipo_doc_attr or 'cotización' in tipo_doc_attr or 'cotizacion' in num_doc_raw.lower() or 'cotización' in num_doc_raw.lower():
        # Limpiamos posibles redundancias de la palabra "Cotización"
        clean_num = num_doc_raw.replace('Cotizacion_', '').replace('cotizacion_', '').replace('Cotizacion', '').replace('cotizacion', '')
        clean_num = clean_num.replace('Cotización_', '').replace('cotización_', '').replace('Cotización', '').replace('cotización', '').strip('_ ')
        filename = f"Cotizacion_{clean_num}_{cliente_slug}.pdf"
        
    else:
        # Por las dudas, si no es ninguno, dejamos un fallback limpio usando el tipo que venga mapeado
        prefijo = tipo_doc_attr.capitalize() if tipo_doc_attr else 'Documento'
        filename = f"{prefijo}_{num_doc_raw.replace(' ', '_')}_{cliente_slug}.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    buffer = generar_pdf_buffer(cotizacion)
    response.write(buffer.getvalue())
    return response

def generar_pdf_factura(factura):
    response = HttpResponse(content_type='application/pdf')
    
    # Extraemos y limpiamos el nombre del cliente de la factura
    cliente_nombre = factura.cliente.nombre if factura.cliente and factura.cliente.nombre else 'sin_nombre'
    cliente_slug = cliente_nombre.strip().replace(' ', '_')
    
    # Formateamos el punto de venta y número tradicionales de la factura
    pv = factura.punto_venta or 0
    numero = factura.numero or 0
    
    # Nombre resultante: factura_0004-00000152_Juan_Perez.pdf
    filename = f"factura_{pv:04d}-{numero:08d}_{cliente_slug}.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    buffer = generar_pdf_factura_buffer(factura)
    response.write(buffer.getvalue())
    return response