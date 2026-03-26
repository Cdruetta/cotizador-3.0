"""
Shim para compatibilidad.

La implementación real de la generación PDF vive en `cotizaciones/utils/pdf_utils.py`.
"""

from .utils.pdf_utils import generar_pdf_cotizacion, generar_pdf_buffer  # noqa: F401
