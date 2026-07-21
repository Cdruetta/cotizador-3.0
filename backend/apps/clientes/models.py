from django.db import models
from simple_history.models import HistoricalRecords


class Cliente(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    localidad = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_cliente"

    def __str__(self):
        return self.nombre

    @property
    def iniciales(self):
        partes = self.nombre.split()
        return "".join(p[0].upper() for p in partes if p)[:2]


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

    nombre = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    empresa = models.CharField(max_length=255, null=True, blank=True)
    cargo = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.NUEVO)
    fuente = models.CharField(max_length=20, choices=Fuente.choices, default=Fuente.WEB)
    notas = models.TextField(null=True, blank=True)
    asignado_a = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "cotizaciones_lead"
