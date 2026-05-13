from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Cotizacion(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ("presupuesto", "Presupuesto"),
        ("recibo", "Recibo"),
    ]

    numero = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Número",
    )
    cliente = models.ForeignKey("Cliente", on_delete=models.CASCADE, verbose_name="Cliente")
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default="presupuesto",
        verbose_name="Tipo de Documento",
    )
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
        verbose_name="Descuento (%)",
    )
    subtotal_bruto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal (sin descuento)",
    )
    monto_descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Monto Descuento",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Total",
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("enviada", "Enviada"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
        ("facturada", "Facturada"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="borrador",
        verbose_name="Estado",
    )
    
    email_enviado = models.BooleanField(default=False, verbose_name="Email enviado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ["-fecha", "-numero"]

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not is_new or self.numero:
            return super().save(*args, **kwargs)

        super().save(*args, **kwargs)
        prefix = "Cotizacion N°" if self.tipo_documento == "presupuesto" else "Recibo N°"
        self.numero = f"{prefix} {self.id}"
        super().save(update_fields=["numero"])

    def calcular_total(self):
        subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal_bruto = subtotal
        descuento = (subtotal * self.descuento_porcentaje / Decimal("100")).quantize(Decimal("0.01"))
        self.monto_descuento = descuento
        self.total = subtotal - descuento
        self.save(update_fields=["subtotal_bruto", "monto_descuento", "total"])
        return self.total

    def get_absolute_url(self):
        return reverse("cotizacion_detail", kwargs={"pk": self.pk})


class CotizacionItem(models.Model):
    cotizacion = models.ForeignKey(
        "Cotizacion",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Cotización",
    )
    producto = models.ForeignKey("Producto", on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Precio Unitario",
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal",
    )

    class Meta:
        verbose_name = "Item de Cotización"
        verbose_name_plural = "Items de Cotización"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.cotizacion.calcular_total()

