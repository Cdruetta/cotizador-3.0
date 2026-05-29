from ...pdf_utils import generar_pdf_cotizacion
from ...utils.pdf_utils_recibo import generar_pdf_recibo_response


def build_cotizacion_pdf_response(*, cotizacion):
    return generar_pdf_cotizacion(cotizacion)


def build_recibo_pdf_response(*, recibo):
    return generar_pdf_recibo_response(recibo)

