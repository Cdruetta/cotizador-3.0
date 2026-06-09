from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def format_cuit_afip(raw: str) -> str:
    """Formatea CUIT con guiones si tiene 11 dígitos."""
    if not raw:
        return ""
    d = "".join(c for c in str(raw) if c.isdigit())
    if len(d) != 11:
        return str(raw).strip()
    return f"{d[:2]}-{d[2:10]}-{d[10]}"


def fmt_ar_num(val, decimales=2):
    """Formatea número con coma decimal (estilo AR)."""
    if val is None:
        return ""
    q = Decimal(str(val)).quantize(Decimal(10) ** -decimales)
    s = format(q, "f")
    if decimales == 0:
        return s.split('.')[0]
    ent, frac = s.split('.')
    return f'{ent},{frac}'


def tipo_factura_afip(letra: str) -> str:
    return {'A': '01', 'B': '06', 'C': '11', 'M': '51'}.get((letra or 'C').upper(), '11')


def styles_factura():
    """Retorna estilos para factura (subset usado por builders)."""
    COLOR_PRIMARY = colors.HexColor('#1C3A5E')
    COLOR_HEADER_TEXT = colors.white
    return {
        'factura_titulo': ParagraphStyle('FacTitulo', fontName='Helvetica-Bold', fontSize=16, textColor=COLOR_PRIMARY, alignment=TA_RIGHT),
        'factura_meta': ParagraphStyle('FacMeta', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#1A1A2E'), alignment=TA_RIGHT),
        'tab_head': ParagraphStyle('FacTabHead', fontName='Helvetica-Bold', fontSize=8, textColor=COLOR_HEADER_TEXT, alignment=TA_CENTER),
    }


def styles():
    """Retorna estilos generales completos usados por _build_elements."""
    return {
        'empresa_nombre': ParagraphStyle('EmpresaNombre', fontName='Helvetica-Bold', fontSize=16),
        'empresa_sub': ParagraphStyle('EmpresaSub', fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#5A6A80')),
        'doc_titulo': ParagraphStyle('DocTitulo', fontName='Helvetica-Bold', fontSize=22, alignment=TA_RIGHT),
        'doc_numero_blanco': ParagraphStyle('DocNumero', fontName='Helvetica', fontSize=14, textColor=colors.white, alignment=TA_RIGHT),
        'seccion': ParagraphStyle('Seccion', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#1C3A5E'), spaceAfter=4),
        'campo_label': ParagraphStyle('CampoLabel', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#5A6A80')),
        'campo_valor': ParagraphStyle('CampoValor', fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#1A1A2E')),
        'tabla_header': ParagraphStyle('TabHead', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=TA_CENTER),
        'tabla_celda': ParagraphStyle('TabCelda', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#1A1A2E')),
        'tabla_derecha': ParagraphStyle('TabDer', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#1A1A2E'), alignment=TA_RIGHT),
        'tabla_total': ParagraphStyle('TabTotal', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1C3A5E'), alignment=TA_RIGHT),
        'obs_titulo': ParagraphStyle('ObsTitulo', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1C3A5E'), spaceAfter=4),
        'obs_texto': ParagraphStyle('ObsTexto', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#1A1A2E'), leading=13),
        'footer_validez': ParagraphStyle('FooterValidez', fontName='Helvetica-Oblique', fontSize=8.5, textColor=colors.HexColor('#5A6A80'), alignment=TA_CENTER),
        'footer_slogan': ParagraphStyle('FooterSlogan', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor('#2E5D8E'), alignment=TA_CENTER),
        'footer_contacto': ParagraphStyle('FooterContacto', fontName='Helvetica', fontSize=7.5, textColor=colors.HexColor('#5A6A80'), alignment=TA_CENTER),
    }
