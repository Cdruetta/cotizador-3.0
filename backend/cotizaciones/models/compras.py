from django.db import models
from django.conf import settings
from .proveedores import Proveedor
from .productos import Producto


class Compra(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("recibida", "Recibida"),
        ("cancelada", "Cancelada"),
    ]

    numero = models.CharField(max_length=50, unique=True, verbose_name="Número")
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor"
    )
    fecha = models.DateField(verbose_name="Fecha")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente", verbose_name="Estado"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha", "-numero"]

    def __str__(self):
        return f"Compra {self.numero} — {self.proveedor.nombre}"

    def save(self, *args, **kwargs):
        if not self.numero:
            last = Compra.objects.all().order_by("-id").first()
            n = (last.id + 1) if last else 1
            self.numero = f"C-{n:04d}"
        super().save(*args, **kwargs)

    def actualizar_totales(self):
        total = self.items.aggregate(total_suma=models.Sum("subtotal"))["total_suma"] or 0
        self.total = total
        self.save()


class CompraItem(models.Model):
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name="items", verbose_name="Compra"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto"
    )
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Item de Compra"
        verbose_name_plural = "Items de Compra"

    def __str__(self):
        return f"{self.producto or self.descripcion} — {self.cantidad} x ${self.precio_unitario}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
