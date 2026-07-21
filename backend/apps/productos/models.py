from django.db import models
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    contacto = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_proveedor"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    TIPO_CHOICES = [
        ("producto", "Producto"),
        ("servicio_soft", "Servicio Software"),
        ("servicio_hard", "Servicio Hardware"),
    ]

    nombre = models.CharField(max_length=255, db_index=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="producto")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.00)])
    stock = models.PositiveIntegerField(default=0, db_index=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_producto"

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_categoria"

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_marca"

    def __str__(self):
        return self.nombre


class ListaPrecio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    porcentaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0, validators=[MinValueValidator(0.00)])
    por_defecto = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        db_table = "cotizaciones_listaprecio"

    def save(self, *args, **kwargs):
        if self.por_defecto:
            ListaPrecio.objects.exclude(pk=self.pk).update(por_defecto=False)
        super().save(*args, **kwargs)


class ListaPrecioItem(models.Model):
    lista = models.ForeignKey(ListaPrecio, on_delete=models.CASCADE, related_name="items")
    categoria = models.CharField(max_length=200)
    servicio = models.CharField(max_length=500)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.00)])
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "categoria", "servicio"]
        db_table = "cotizaciones_listaprecioitem"
