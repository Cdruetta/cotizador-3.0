from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class ListaPrecio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    porcentaje = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Porcentaje de recargo",
        help_text="Porcentaje de recargo sobre el precio unitario del producto",
        default=0,
        blank=True,
    )
    por_defecto = models.BooleanField(default=False, verbose_name="Por defecto",
                                      help_text="Se usará automáticamente para nuevos clientes")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Lista de precio"
        verbose_name_plural = "Listas de precio"
        ordering = ["nombre"]

    def __str__(self):
        if self.porcentaje:
            return f"{self.nombre} ({self.porcentaje}%)"
        return self.nombre

    def save(self, *args, **kwargs):
        if self.por_defecto:
            ListaPrecio.objects.filter(por_defecto=True).exclude(pk=self.pk).update(por_defecto=False)
        super().save(*args, **kwargs)


class ListaPrecioItem(models.Model):
    lista = models.ForeignKey(ListaPrecio, on_delete=models.CASCADE, related_name="items", verbose_name="Lista de precio")
    categoria = models.CharField(max_length=200, verbose_name="Categoría")
    servicio = models.CharField(max_length=500, verbose_name="Servicio")
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Precio (ARS)",
    )
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Item de lista de precio"
        verbose_name_plural = "Items de lista de precio"
        ordering = ["orden", "categoria", "servicio"]

    def __str__(self):
        return f"{self.categoria} - {self.servicio}: ${self.precio}"
