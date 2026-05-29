from django.db import models
from django.conf import settings


class Lead(models.Model):
    class Estado(models.TextChoices):
        NUEVO = "nuevo", "Nuevo"
        CONTACTADO = "contactado", "Contactado"
        CALIFICADO = "calificado", "Calificado"
        PROPUESTA = "propuesta", "Propuesta"
        NEGOCIACION = "negociacion", "Negociación"
        GANADO = "ganado", "Ganado"
        PERDIDO = "perdido", "Perdido"

    class Fuente(models.TextChoices):
        WEB = "web", "Web"
        REFERRAL = "referral", "Referido"
        LLAMADA = "llamada", "Llamada"
        EMAIL = "email", "Email"
        REDES_SOCIALES = "redes_sociales", "Redes Sociales"
        WHATSAPP = "whatsapp", "WhatsApp"
        OTRO = "otro", "Otro"

    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    empresa = models.CharField(max_length=255, blank=True, null=True, verbose_name="Empresa")
    cargo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cargo")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.NUEVO,
        verbose_name="Estado",
    )
    fuente = models.CharField(
        max_length=20,
        choices=Fuente.choices,
        default=Fuente.WEB,
        verbose_name="Fuente",
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Asignado a",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ["-created_at"]

    def __str__(self):
        return self.nombre
