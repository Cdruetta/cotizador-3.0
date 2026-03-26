from django.db import models


class Configuracion(models.Model):
    ciudad_nombre = models.CharField(max_length=100, default="Río Cuarto", verbose_name="Ciudad")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, default=-33.130000, verbose_name="Latitud")
    longitud = models.DecimalField(max_digits=9, decimal_places=6, default=-64.350000, verbose_name="Longitud")
    empresa_nombre = models.CharField(max_length=100, default="GCinsumos", verbose_name="Nombre empresa")
    empresa_direccion = models.CharField(max_length=200, default="", verbose_name="Dirección")
    empresa_telefono = models.CharField(max_length=30, default="", verbose_name="Teléfono")
    empresa_email = models.EmailField(blank=True, default="", verbose_name="Email empresa")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuración"

    def __str__(self):
        return f"Configuración del sistema ({self.ciudad_nombre})"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

