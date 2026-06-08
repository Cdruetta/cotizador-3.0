"""Merge migration resolving divergent leaf nodes.

This migration merges two independent heads created during development:
- 0021_alter_listaprecio_porcentaje_listaprecioitem
- 0090_auto_add_indexes

It has no operations; its purpose is to join the migration graph so
`makemigrations`/`migrate` see a single head.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cotizaciones", "0021_alter_listaprecio_porcentaje_listaprecioitem"),
        ("cotizaciones", "0090_auto_add_indexes"),
    ]

    operations = []
