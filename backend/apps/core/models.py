from django.db import models


class Configuracion(models.Model):
    ciudad_nombre = models.CharField(max_length=100, default="Río Cuarto")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, default=-33.130000)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, default=-64.350000)
    empresa_nombre = models.CharField(max_length=100, default="GCinsumos")
    empresa_direccion = models.CharField(max_length=200, default="")
    empresa_telefono = models.CharField(max_length=30, default="")
    empresa_email = models.EmailField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Configuración"
        db_table = "cotizaciones_configuracion"

    @classmethod
    def get(cls):
        return cls.objects.get_or_create(pk=1)[0]
