from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal


# ==========================
# CLIENTES
# ==========================
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
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================
# PROVEEDORES
# ==========================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Persona de Contacto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================
# PRODUCTOS
# ==========================
class Producto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario",
        default=0
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, verbose_name="Proveedor")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================
# COTIZACIONES
# ==========================
class Cotizacion(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('presupuesto', 'Presupuesto'),
        ('recibo', 'Recibo'),
    ]

    numero = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Número"
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='presupuesto',
        verbose_name="Tipo de Documento"
    )
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    # --- DESCUENTO (nuevo) ---
    descuento_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Descuento (%)"
    )

    subtotal_bruto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal (sin descuento)"
    )
    monto_descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Monto Descuento"
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total"
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    completada = models.BooleanField(default=False, verbose_name="Completada", db_column="completado")
    email_enviado = models.BooleanField(default=False, verbose_name="Email enviado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        desired_prefix = 'Cotizacion N°' if self.tipo_documento == 'presupuesto' else 'Recibo N°'
        desired_value = f"{desired_prefix} {self.id}"
        if not self.numero or self.numero != desired_value:
            self.numero = desired_value
            super().save(update_fields=['numero'])

    def calcular_total(self):
        """Recalcula subtotal, descuento y total."""
        subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal_bruto = subtotal
        descuento = (subtotal * self.descuento_porcentaje / Decimal('100')).quantize(Decimal('0.01'))
        self.monto_descuento = descuento
        self.total = subtotal - descuento
        self.save(update_fields=['subtotal_bruto', 'monto_descuento', 'total'])
        return self.total

    def get_absolute_url(self):
        return reverse("cotizacion_detail", kwargs={"pk": self.pk})


# ==========================
# ITEMS DE COTIZACION
# ==========================
class CotizacionItem(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Cotización"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal"
    )

    class Meta:
        verbose_name = "Item de Cotización"
        verbose_name_plural = "Items de Cotización"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.cotizacion.calcular_total()

# ==========================
# CONFIGURACION DEL SISTEMA
# ==========================
class Configuracion(models.Model):
    ciudad_nombre = models.CharField(max_length=100, default='Río Cuarto', verbose_name='Ciudad')
    latitud = models.DecimalField(max_digits=9, decimal_places=6, default=-33.130000, verbose_name='Latitud')
    longitud = models.DecimalField(max_digits=9, decimal_places=6, default=-64.350000, verbose_name='Longitud')
    empresa_nombre = models.CharField(max_length=100, default='GCinsumos', verbose_name='Nombre empresa')
    empresa_direccion = models.CharField(max_length=200, default='', verbose_name='Dirección')
    empresa_telefono = models.CharField(max_length=30, default='', verbose_name='Teléfono')
    empresa_email = models.EmailField(blank=True, default='', verbose_name='Email empresa')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuración'

    def __str__(self):
        return f'Configuración del sistema ({self.ciudad_nombre})'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj