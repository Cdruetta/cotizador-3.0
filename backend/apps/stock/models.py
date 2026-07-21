from django.db import models


class MovimientoStock(models.Model):
    TIPO_CHOICES = [("entrada", "Entrada"), ("salida", "Salida"), ("ajuste", "Ajuste")]

    producto = models.ForeignKey("productos.Producto", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    stock_resultante = models.PositiveIntegerField(default=0)
    motivo = models.TextField(null=True, blank=True)
    usuario = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "cotizaciones_movimientostock"
