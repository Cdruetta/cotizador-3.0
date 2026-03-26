from ...pdf_utils import generar_pdf_cotizacion


def build_cotizacion_pdf_response(*, cotizacion):
    return generar_pdf_cotizacion(cotizacion)

