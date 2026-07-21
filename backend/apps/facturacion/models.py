from decimal import Decimal
from django.db import models
from simple_history.models import HistoricalRecords


class ConfiguracionAFIP(models.Model):
    AMBIENTE_CHOICES = [("homologacion", "Homologación"), ("produccion", "Producción")]

    cuit = models.CharField(max_length=13)
    razon_social = models.CharField(max_length=255)
    domicilio = models.CharField(max_length=255, blank=True)
    punto_venta = models.IntegerField(default=1)
    ambiente = models.CharField(max_length=15, choices=AMBIENTE_CHOICES, default="homologacion")
    certificado = models.FileField(upload_to="certs/", null=True, blank=True)
    clave_privada = models.FileField(upload_to="certs/", null=True, blank=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cotizaciones_configuracionafip"

    @classmethod
    def get_config(cls):
        return cls.objects.first()


class Factura(models.Model):
    TIPO_CHOICES = [("C", "Factura C")]
    ESTADO_CHOICES = [("borrador", "Borrador"), ("autorizada", "Autorizada"), ("anulada", "Anulada")]

    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="facturas")
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default="C")
    punto_venta = models.IntegerField(default=1)
    numero = models.IntegerField(null=True, blank=True, db_index=True)
    fecha = models.DateField(auto_now_add=True)
    neto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cae = models.CharField(max_length=14, blank=True)
    cae_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="borrador")
    creada = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-creada"]
        db_table = "cotizaciones_factura"

    def actualizar_totales(self):
        items = self.items.all()
        self.total = sum(i.subtotal for i in items)
        self.neto = self.total
        self.save(update_fields=["total", "neto"])


class ItemFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="items")
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "cotizaciones_itemfactura"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * Decimal(str(self.precio_unit))
        super().save(*args, **kwargs)
