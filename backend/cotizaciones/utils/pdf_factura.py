import json
import base64
import os
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

import qrcode
from django.conf import settings
from reportlab.lib import colors
from django.http import HttpResponse
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable,
)

from ..models import ConfiguracionAFIP
from .pdf_colors import (
    COLOR_BORDER, COLOR_HEADER_BG, COLOR_HEADER_TEXT,
    COLOR_PRIMARY, COLOR_ROW_ALT, COLOR_ROW_HEADER,
    COLOR_SECONDARY, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_TOTAL_BG,
)
from ..services.documents.pdf_helpers import (
    format_cuit_afip, fmt_ar_num, tipo_factura_afip, styles_factura,
)

FACTURA_EMPRESA_NOMBRE = 'GCinsumos'
FACTURA_LEYENDA_MONOTRIBUTO = 'RESPONSABLE MONOTRIBUTO'

_format_cuit_afip = format_cuit_afip
_fmt_ar_num = fmt_ar_num
_tipo_factura_afip = tipo_factura_afip


def _factura_logo_path():
    for name in ('logo_factura.png', 'logo.png'):
        p = os.path.join(settings.BASE_DIR, 'static', 'images', name)
        if os.path.exists(p):
            return p
    return None


def _factura_qr_image(factura):
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
    elements = []
    config = ConfiguracionAFIP.get_config()
    razon_social = (config.razon_social if config else '') or FACTURA_EMPRESA_NOMBRE
    cuit_emitter = _format_cuit_afip(config.cuit) if config else ''
    domicilio_emitter = (config.domicilio if config else '') or ''
    letra = (factura.tipo or 'C').upper()
    pw = 6.5 * inch

    s_emp = ParagraphStyle('FE', fontName='Helvetica-Bold', fontSize=13, textColor=COLOR_PRIMARY, leading=16)
    s_info = ParagraphStyle('FI', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_factura_tit = ParagraphStyle('FFT', fontName='Helvetica-Bold', fontSize=20, textColor=COLOR_PRIMARY, alignment=TA_CENTER, leading=24)
    s_factura_letra = ParagraphStyle('FFL', fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_SECONDARY, alignment=TA_CENTER, leading=17)
    s_meta_lbl = ParagraphStyle('FML', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT_MUTED, alignment=TA_RIGHT, leading=9)
    s_meta_val = ParagraphStyle('FMV', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=13)
    s_cli_tit = ParagraphStyle('FCT', fontName='Helvetica-Bold', fontSize=9, textColor=COLOR_PRIMARY, leading=12)
    s_cli_val = ParagraphStyle('FCV', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, leading=12)
    s_th = ParagraphStyle('FTH', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER, leading=10)
    s_th_l = ParagraphStyle('FTHL', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_HEADER_TEXT, leading=10)
    s_td = ParagraphStyle('FTD', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_tdr = ParagraphStyle('FTDR', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=10)
    s_tdc = ParagraphStyle('FTDC', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, alignment=TA_CENTER, leading=10)
    s_tot_lbl = ParagraphStyle('FTL', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=13)
    s_tot_val = ParagraphStyle('FTV', fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_PRIMARY, alignment=TA_RIGHT, leading=17)
    s_sub_lbl = ParagraphStyle('FSL', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=11)
    s_sub_val = ParagraphStyle('FSV', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=11)
    s_cae = ParagraphStyle('FCAE', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_cae_bold = ParagraphStyle('FCAEB', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_TEXT, leading=10)
    s_arca = ParagraphStyle('FARCA', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT_MUTED, leading=9)
    s_footer = ParagraphStyle('FPT', fontName='Helvetica', fontSize=7, textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=9)
    s_moneda = ParagraphStyle('FMON', fontName='Helvetica', fontSize=8, textColor=COLOR_TEXT_MUTED, alignment=TA_CENTER, leading=10)

    elements.append(Paragraph('FACTURA', s_factura_tit))
    elements.append(Paragraph(f'<b>{letra}</b>', s_factura_letra))
    elements.append(Spacer(1, 8))

    left_cells = []
    logo_path = _factura_logo_path()
    if logo_path:
        ir = ImageReader(logo_path)
        iw, ih = ir.getSize()
        logo_w = 0.9 * inch
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

    col_left = Table([[c] for c in left_cells], colWidths=[3.8 * inch])
    col_left.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    pv = factura.punto_venta or 0
    num = factura.numero or 0
    fecha_txt = factura.fecha.strftime('%d/%m/%Y')
    s_meta_line = ParagraphStyle('FML2', fontName='Helvetica', fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=13)
    right_inner = Table([
        [Paragraph(f'Punto de Venta: <b>{pv:04d}</b>', s_meta_line)],
        [Paragraph(f'Comp. N°: <b>{num:08d}</b>', s_meta_line)],
        [Paragraph(f'Fecha de Emisión: <b>{fecha_txt}</b>', s_meta_line)],
    ], colWidths=[2.2 * inch])
    right_inner.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    header_tbl = Table([[col_left, right_inner]], colWidths=[4.1 * inch, 2.4 * inch])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_tbl)

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

    data_rows = len(table_data)
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
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    items_table.setStyle(TableStyle(ts))
    elements.append(items_table)

    elements.append(Spacer(1, 6))
    s_total_line = ParagraphStyle('FTL2', fontName='Helvetica', fontSize=10, textColor=COLOR_TEXT, alignment=TA_RIGHT, leading=14)
    s_total_num = ParagraphStyle('FTN2', fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_PRIMARY, alignment=TA_RIGHT, leading=17)
    tot_data = [
        [Paragraph(f'SUBTOTAL:  ${_fmt_ar_num(neto, 2)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', s_total_line),
         Paragraph(f'DESCUENTO:  ${_fmt_ar_num(descuento, 2)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', s_total_line),
         Paragraph(f'TOTAL:  ${_fmt_ar_num(total, 2)}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;', s_total_num)],
    ]
    tot_col_w = [pw * 0.3, pw * 0.3, pw * 0.4]
    tot_tbl = Table(tot_data, colWidths=tot_col_w)
    tot_tbl.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, COLOR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_TOTAL_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    elements.append(tot_tbl)

    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Moneda: PESOS ($) — Todos los importes están expresados en Pesos Argentinos', s_moneda))
    if not cuit_cli and total >= Decimal('10000000'):
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(
            '<i>Importe >= $10.000.000 — obligatorio informar DNI/CUIT/CUIL/CDI del comprador</i>',
            s_moneda,
        ))

    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=COLOR_BORDER, spaceAfter=8))

    if factura.estado == 'autorizada' and factura.cae:
        vto = factura.cae_vencimiento.strftime('%d/%m/%Y') if factura.cae_vencimiento else '—'
        qr_buf = _factura_qr_image(factura)
        if qr_buf:
            qr_img = Image(qr_buf, width=0.7 * inch, height=0.7 * inch)
            cae_lines = [
                f'CAE: <b>{factura.cae}</b>',
                f'Vto. CAE: <b>{vto}</b>',
                '<br/>',
                'Comprobante autorizado por ARCA (ex AFIP)',
            ]
            if domicilio_emitter:
                cae_lines.append(f'<br/>{escape(domicilio_emitter)}')
            cae_par = Paragraph('<br/>'.join(cae_lines), s_cae)
            footer_row = Table([[qr_img, cae_par]], colWidths=[0.85 * inch, pw - 0.85 * inch])
            footer_row.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
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
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_pdf_factura(factura):
    response = HttpResponse(content_type='application/pdf')

    cliente_nombre = factura.cliente.nombre if factura.cliente and factura.cliente.nombre else 'sin_nombre'
    cliente_slug = cliente_nombre.strip().replace(' ', '_')

    pv = factura.punto_venta or 0
    numero = factura.numero or 0

    filename = f"factura_{pv:04d}-{numero:08d}_{cliente_slug}.pdf"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    buffer = generar_pdf_factura_buffer(factura)
    response.write(buffer.getvalue())
    return response
