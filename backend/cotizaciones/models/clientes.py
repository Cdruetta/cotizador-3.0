from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    localidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localidad")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

