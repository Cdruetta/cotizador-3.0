from django.db import models
from django.db.models import Sum
from .clientes import Cliente
from simple_history.models import HistoricalRecords

class ConfiguracionAFIP(models.Model):
    AMBIENTE_CHOICES = [
        ('homologacion', 'Homologación (pruebas)'),
        ('produccion', 'Producción'),
    ]
    cuit          = models.CharField(max_length=13)
    razon_social  = models.CharField(max_length=255)
    domicilio     = models.CharField(max_length=255, blank=True)
    punto_venta   = models.IntegerField(default=1)
    ambiente      = models.CharField(max_length=15, choices=AMBIENTE_CHOICES, default='homologacion')
    certificado   = models.FileField(upload_to='certs/', blank=True, null=True)
    clave_privada = models.FileField(upload_to='certs/', blank=True, null=True)
    actualizado   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración ARCA'

    def __str__(self):
        return f"{self.razon_social} ({self.cuit})"

    @classmethod
    def get_config(cls):
        return cls.objects.first()


class Factura(models.Model):
    TIPO_CHOICES = [('C', 'Factura C')]
    ESTADO_CHOICES = [
        ('borrador',   'Borrador'),
        ('autorizada', 'Autorizada por ARCA'),
        ('anulada',    'Anulada'),
    ]

    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas')
    tipo            = models.CharField(max_length=1, choices=TIPO_CHOICES, default='C')
    punto_venta     = models.IntegerField(default=1)
    numero          = models.IntegerField(null=True, blank=True, db_index=True)
    fecha           = models.DateField(auto_now_add=True)
    neto            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cae             = models.CharField(max_length=14, blank=True)
    cae_vencimiento = models.DateField(null=True, blank=True)
    estado          = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='borrador')
    creada          = models.DateTimeField(auto_now_add=True)
    usuario         = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-creada']
        verbose_name = 'Factura'

    def __str__(self):
        return f"Factura C {self.punto_venta:04d}-{self.numero or 0:08d}"

    def actualizar_totales(self):
        """Calcula la suma de subtotales y actualiza la factura."""
        resultado = self.items.aggregate(total_suma=Sum('subtotal'))['total_suma'] or 0
        self.total = resultado
        self.neto = resultado  # En Factura C coinciden
        self.save()


class ItemFactura(models.Model):
    factura     = models.ForeignKey(Factura, related_name='items', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    cantidad    = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal    = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unit
        super().save(*args, **kwargs)
