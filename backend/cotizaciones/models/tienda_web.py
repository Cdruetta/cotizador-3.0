from django.db import models


class TiendaWebConfig(models.Model):
    activa = models.BooleanField(default=False, verbose_name="Tienda activa")
    nombre_tienda = models.CharField(max_length=200, blank=True, default="", verbose_name="Nombre de la tienda")
    descripcion = models.TextField(blank=True, default="", verbose_name="Descripción")
    email_contacto = models.EmailField(blank=True, default="", verbose_name="Email de contacto")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Configuración de tienda web"
        verbose_name_plural = "Configuraciones de tienda web"

    def __str__(self):
        return self.nombre_tienda or "Tienda Web"
