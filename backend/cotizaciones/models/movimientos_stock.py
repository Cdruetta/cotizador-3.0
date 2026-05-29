from django.db import models
from django.conf import settings
from .productos import Producto


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
        ("ajuste", "Ajuste"),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, verbose_name="Producto"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    stock_resultante = models.PositiveIntegerField(default=0, verbose_name="Stock resultante")
    motivo = models.TextField(blank=True, null=True, verbose_name="Motivo")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.producto.nombre} x {self.cantidad}"
