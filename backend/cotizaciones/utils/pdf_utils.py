from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable,
)

from .pdf_colors import (
    COLOR_ACCENT, COLOR_BORDER, COLOR_FOOTER_LINE,
    COLOR_HEADER_BG, COLOR_HEADER_TEXT, COLOR_PRIMARY,
    COLOR_ROW_ALT, COLOR_ROW_HEADER, COLOR_SECONDARY,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_TOTAL_BG,
)
from .pdf_cotizacion import (
    _build_elements, generar_pdf_buffer, generar_pdf_cotizacion,
)
from .pdf_factura import (
    FACTURA_EMPRESA_NOMBRE, FACTURA_LEYENDA_MONOTRIBUTO,
    _build_elements_factura, _factura_logo_path, _factura_qr_image,
    _factura_watermark_and_frame, generar_pdf_factura_buffer,
    generar_pdf_factura,
)
