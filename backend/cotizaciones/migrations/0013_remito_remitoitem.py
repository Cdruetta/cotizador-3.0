from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0012_lead"),
    ]

    operations = [
        migrations.CreateModel(
            name="Remito",
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
                    "direccion_entrega",
                    models.TextField(
                        blank=True, null=True, verbose_name="Dirección de entrega"
                    ),
                ),
                (
                    "observaciones",
                    models.TextField(
                        blank=True, null=True, verbose_name="Observaciones"
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("entregado", "Entregado"),
                            ("cancelado", "Cancelado"),
                        ],
                        default="pendiente",
                        max_length=20,
                        verbose_name="Estado",
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
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cotizaciones.cliente",
                        verbose_name="Cliente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Remito",
                "verbose_name_plural": "Remitos",
                "ordering": ["-fecha", "-numero"],
            },
        ),
        migrations.CreateModel(
            name="RemitoItem",
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
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Descripción",
                    ),
                ),
                (
                    "cantidad",
                    models.PositiveIntegerField(
                        default=1, verbose_name="Cantidad"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creado"
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
                (
                    "remito",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="cotizaciones.remito",
                        verbose_name="Remito",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item de Remito",
                "verbose_name_plural": "Items de Remito",
            },
        ),
    ]
