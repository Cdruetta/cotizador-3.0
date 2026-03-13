from django.db import migrations, models
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):
    """
    Agrega campos de descuento y email_enviado a Cotizacion.
    Compatible con PostgreSQL en Railway.
    Los campos stock y precio_unitario de Producto ya existen desde 0002.
    """

    dependencies = [
        ('cotizaciones', '0004_cotizacion_completada'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacion',
            name='descuento_porcentaje',
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=Decimal('0.00'),
                validators=[
                    django.core.validators.MinValueValidator(Decimal('0.00')),
                    django.core.validators.MaxValueValidator(Decimal('100.00')),
                ],
                verbose_name='Descuento (%)',
            ),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='subtotal_bruto',
            field=models.DecimalField(
                max_digits=12,
                decimal_places=2,
                default=Decimal('0.00'),
                verbose_name='Subtotal (sin descuento)',
            ),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='monto_descuento',
            field=models.DecimalField(
                max_digits=12,
                decimal_places=2,
                default=Decimal('0.00'),
                verbose_name='Monto Descuento',
            ),
        ),
        migrations.AddField(
            model_name='cotizacion',
            name='email_enviado',
            field=models.BooleanField(
                default=False,
                verbose_name='Email enviado',
            ),
        ),
    ]
