from django.db import migrations


MODELS = [
    "Categoria",
    "Cliente",
    "Compra",
    "CompraItem",
    "Configuracion",
    "ConfiguracionAFIP",
    "Cotizacion",
    "CotizacionItem",
    "Factura",
    "ItemFactura",
    "Lead",
    "ListaPrecio",
    "ListaPrecioItem",
    "Marca",
    "MovimientoStock",
    "Producto",
    "Proveedor",
    "Recibo",
    "ReciboItem",
    "Remito",
    "RemitoItem",
]


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0092_delete_tiendawebconfig"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name=m)
                for m in MODELS
            ],
        ),
    ]
