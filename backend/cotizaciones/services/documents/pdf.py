def build_cotizacion_pdf_response(*, cotizacion):
    # Import lazily to avoid circular imports at module import time
    from ...utils.pdf_utils import generar_pdf_cotizacion

    return generar_pdf_cotizacion(cotizacion)


def build_recibo_pdf_response(*, recibo):
    # Import lazily to avoid circular imports at module import time
    from ...utils.pdf_utils_recibo import generar_pdf_recibo_response

    return generar_pdf_recibo_response(recibo)

