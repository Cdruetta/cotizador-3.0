from django.conf import settings
from django.core.mail import EmailMessage


def enviar_cotizacion_por_email(*, cotizacion, email_destino: str, asunto: str, mensaje: str):
    from ...utils.pdf_utils import generar_pdf_buffer
    pdf_buffer = generar_pdf_buffer(cotizacion)
    email = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino],
    )
    email.attach(f"cotizacion_{cotizacion.numero}.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send()


def enviar_recibo_por_email(*, recibo, email_destino: str, asunto: str, mensaje: str):
    from ...utils.pdf_utils_recibo import generar_pdf_recibo_buffer
    pdf_buffer = generar_pdf_recibo_buffer(recibo)
    email = EmailMessage(
        subject=asunto,
        body=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino],
    )
    email.attach(f"recibo_{recibo.numero}.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send()

