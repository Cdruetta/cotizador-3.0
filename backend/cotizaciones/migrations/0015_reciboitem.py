from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0014_recibo"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReciboItem",
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
                    "recibo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="cotizaciones.recibo",
                        verbose_name="Recibo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item de Recibo",
                "verbose_name_plural": "Items de Recibo",
            },
        ),
    ]
