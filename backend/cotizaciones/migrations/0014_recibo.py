from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0013_remito_remitoitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recibo",
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
                    "forma_pago",
                    models.CharField(
                        choices=[
                            ("efectivo", "Efectivo"),
                            ("transferencia", "Transferencia"),
                            ("cheque", "Cheque"),
                            ("tarjeta_debito", "Tarjeta de Débito"),
                            ("tarjeta_credito", "Tarjeta de Crédito"),
                            ("mercadopago", "Mercado Pago"),
                            ("otro", "Otro"),
                        ],
                        max_length=20,
                        verbose_name="Forma de pago",
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
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cotizaciones.cliente",
                        verbose_name="Cliente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recibo",
                "verbose_name_plural": "Recibos",
                "ordering": ["-fecha", "-numero"],
            },
        ),
    ]
