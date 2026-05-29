from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0010_remove_cotizacion_completada_cotizacion_estado"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="activo",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
    ]
