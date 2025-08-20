from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal

# Validador de teléfono: solo números, permite opcionalmente "+" inicial (internacional)
telefono_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Ingrese un teléfono válido con solo números (opcional '+' al inicio)."
)

# Validador de solo números (para otros usos si quieres)
solo_numeros = RegexValidator(r'^\d+$', 'Solo se permiten números.')

class Cliente(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    direccion = models.CharField(max_length=300, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, validators=[telefono_validator], verbose_name="Teléfono")
    localidad = models.CharField(max_length=100, blank=True, verbose_name="Localidad")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    direccion = models.CharField(max_length=300, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, validators=[telefono_validator], verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    contacto = models.CharField(max_length=100, blank=True, verbose_name="Persona de Contacto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio Unitario"
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cotizacion(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('presupuesto', 'Presupuesto'),
        ('recibo', 'Recibo'),
    ]

    numero = models.CharField(max_length=20, unique=True, verbose_name="Número")
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

    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save()
        return total


class CotizacionItem(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Cotización"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Cantidad"
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Item de Cotización"
        verbose_name_plural = "Items de Cotización"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.cotizacion.calcular_total()

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"
