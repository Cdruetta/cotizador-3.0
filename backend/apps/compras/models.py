from django.db import models


class Compra(models.Model):
    ESTADO_CHOICES = [("pendiente", "Pendiente"), ("recibida", "Recibida"), ("cancelada", "Cancelada")]

    numero = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey("productos.Proveedor", on_delete=models.CASCADE)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    observaciones = models.TextField(null=True, blank=True)
    usuario = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-numero"]
        db_table = "cotizaciones_compra"

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Compra.objects.order_by("-id").first()
            n = (ultimo.id + 1) if ultimo else 1
            self.numero = f"C-{n:04d}"
        super().save(*args, **kwargs)

    def actualizar_totales(self):
        self.total = sum(i.subtotal for i in self.items.all())
        self.save(update_fields=["total"])


class CompraItem(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey("productos.Producto", on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "cotizaciones_compraitem"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
