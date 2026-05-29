from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0017_marca"),
    ]

    operations = [
        migrations.CreateModel(
            name="Compra",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "numero",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Número"
                    ),
                ),
                ("fecha", models.DateField(verbose_name="Fecha")),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="Total"
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("recibida", "Recibida"),
                            ("cancelada", "Cancelada"),
                        ],
                        default="pendiente",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "observaciones",
                    models.TextField(
                        blank=True, null=True, verbose_name="Observaciones"
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creado"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Actualizado"
                    ),
                ),
                (
                    "proveedor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cotizaciones.proveedor",
                        verbose_name="Proveedor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Compra",
                "verbose_name_plural": "Compras",
                "ordering": ["-fecha", "-numero"],
            },
        ),
        migrations.CreateModel(
            name="CompraItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "descripcion",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Descripción"
                    ),
                ),
                (
                    "cantidad",
                    models.PositiveIntegerField(
                        default=1, verbose_name="Cantidad"
                    ),
                ),
                (
                    "precio_unitario",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Precio unitario",
                    ),
                ),
                (
                    "subtotal",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Subtotal",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creado"
                    ),
                ),
                (
                    "compra",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="cotizaciones.compra",
                        verbose_name="Compra",
                    ),
                ),
                (
                    "producto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cotizaciones.producto",
                        verbose_name="Producto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item de Compra",
                "verbose_name_plural": "Items de Compra",
            },
        ),
    ]
