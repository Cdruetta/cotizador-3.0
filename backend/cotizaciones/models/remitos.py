from django.db import models
from django.conf import settings


class Remito(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    numero = models.CharField(max_length=50, unique=True, verbose_name="Número")
    cliente = models.ForeignKey(
        "Cliente",
        on_delete=models.CASCADE,
        verbose_name="Cliente",
    )
    fecha = models.DateField(verbose_name="Fecha")
    direccion_entrega = models.TextField(blank=True, null=True, verbose_name="Dirección de entrega")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Usuario",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Remito"
        verbose_name_plural = "Remitos"
        ordering = ["-fecha", "-numero"]

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        if not self.numero:
            last = Remito.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.numero = f"R-{next_id:04d}"
        super().save(*args, **kwargs)


class RemitoItem(models.Model):
    remito = models.ForeignKey(
        Remito,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Remito",
    )
    producto = models.ForeignKey(
        "Producto",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Producto",
    )
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Item de Remito"
        verbose_name_plural = "Items de Remito"

    def __str__(self):
        return f"{self.descripcion or self.producto} x {self.cantidad}"
