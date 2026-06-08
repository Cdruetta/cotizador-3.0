"""Create indexes for frequently searched fields using CONCURRENTLY.

This migration uses raw SQL to create the indexes with CREATE INDEX CONCURRENTLY
to avoid long table locks on large production tables. The migration is
non-transactional (atomic = False) because Postgres does not allow CREATE INDEX
CONCURRENTLY inside a transaction block.

If you prefer to run these index creations manually on the DB, do not apply
this migration automatically in production.
"""

from django.db import migrations


class Migration(migrations.Migration):
    # Must run outside a transaction so CONCURRENTLY is allowed
    atomic = False

    dependencies = [
        # Ensure this index migration runs after the current app head (0021)
        ('cotizaciones', '0021_alter_listaprecio_porcentaje_listaprecioitem'),
        # Also depend explicitly on recibo creation so the model exists when altering
        ('cotizaciones', '0014_recibo'),
    ]

    def _create_indexes(apps, schema_editor):
        # Ensure autocommit mode so CREATE INDEX CONCURRENTLY is allowed
        conn = schema_editor.connection
        try:
            # Django DB-API wrapper provides set_autocommit
            conn.set_autocommit(True)
        except Exception:
            pass

        stmts = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_cliente_nombre ON cotizaciones_cliente (nombre);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_cliente_email ON cotizaciones_cliente (email);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_producto_nombre ON cotizaciones_producto (nombre);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_producto_stock ON cotizaciones_producto (stock);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_cotizacion_numero ON cotizaciones_cotizacion (numero);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_factura_numero ON cotizaciones_factura (numero);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cotizaciones_recibo_numero ON cotizaciones_recibo (numero);",
        ]

        with conn.cursor() as cur:
            for s in stmts:
                cur.execute(s)


    def _drop_indexes(apps, schema_editor):
        conn = schema_editor.connection
        try:
            conn.set_autocommit(True)
        except Exception:
            pass

        stmts = [
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_cliente_nombre;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_cliente_email;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_producto_nombre;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_producto_stock;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_cotizacion_numero;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_factura_numero;",
            "DROP INDEX CONCURRENTLY IF EXISTS idx_cotizaciones_recibo_numero;",
        ]

        with conn.cursor() as cur:
            for s in stmts:
                cur.execute(s)

    operations = [
        migrations.RunPython(_create_indexes, reverse_code=_drop_indexes),
    ]
