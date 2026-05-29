from django.db import models
from django.conf import settings
from .clientes import Cliente
from .productos import Producto


class Recibo(models.Model):
    FORMA_PAGO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("cheque", "Cheque"),
        ("tarjeta_debito", "Tarjeta de Débito"),
        ("tarjeta_credito", "Tarjeta de Crédito"),
        ("mercadopago", "Mercado Pago"),
        ("otro", "Otro"),
    ]

    numero = models.CharField(max_length=50, unique=True, verbose_name="Número")
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, verbose_name="Cliente"
    )
    fecha = models.DateField(verbose_name="Fecha")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
    forma_pago = models.CharField(
        max_length=20, choices=FORMA_PAGO_CHOICES, verbose_name="Forma de pago"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Recibo"
        verbose_name_plural = "Recibos"
        ordering = ["-fecha", "-numero"]

    def __str__(self):
        return f"Recibo {self.numero} — {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        if not self.numero:
            last = Recibo.objects.all().order_by("-id").first()
            n = (last.id + 1) if last else 1
            self.numero = f"RC-{n:04d}"
        super().save(*args, **kwargs)

    def actualizar_totales(self):
        total = self.items.aggregate(total_suma=models.Sum("subtotal"))["total_suma"] or 0
        self.total = total
        self.save()


class ReciboItem(models.Model):
    recibo = models.ForeignKey(
        Recibo, on_delete=models.CASCADE, related_name="items", verbose_name="Recibo"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto"
    )
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Item de Recibo"
        verbose_name_plural = "Items de Recibo"

    def __str__(self):
        return f"{self.producto or self.descripcion} — {self.cantidad} x ${self.precio_unitario}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
