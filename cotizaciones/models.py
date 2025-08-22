from django.db import models
from django.core.validators import MinValueValidator
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
    localidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localidad")  # <-- agregado
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
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio"
    )
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
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total"
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        """
        Genera el número de cotización automáticamente basado en el ID.
        Ejemplo: COT-1, COT-2, etc.
        """
        super().save(*args, **kwargs)  # primero guarda para tener el ID
        if not self.numero:
            self.numero = f"COT-{self.id}"
            super().save(update_fields=['numero'])

    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save(update_fields=['total'])
        return total

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
