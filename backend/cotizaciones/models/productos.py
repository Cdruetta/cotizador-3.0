from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Precio Unitario",
        default=0,
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    proveedor = models.ForeignKey("Proveedor", on_delete=models.CASCADE, verbose_name="Proveedor")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

