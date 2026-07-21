from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0091_merge_0021_0090"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TiendaWebConfig",
        ),
    ]
