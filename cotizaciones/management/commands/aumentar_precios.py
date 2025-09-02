from decimal import Decimal
from django.core.management.base import BaseCommand
from cotizaciones.models import Producto
import json
import os

class Command(BaseCommand):
    help = "Aumenta todos los precios de productos por un porcentaje y guarda un respaldo previo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--porcentaje",
            type=float,
            default=10.0,  # <--- cambiar el % para subir los precios
            help="Porcentaje de aumento a aplicar a los precios"
        )

    def handle(self, *args, **kwargs):
        porcentaje_aumento = kwargs["porcentaje"]
        factor = 1 + (porcentaje_aumento / 100)

        # -------------------------------
        # Respaldo de precios actuales
        # -------------------------------
        respaldo = {}
        for producto in Producto.objects.all():
            respaldo[producto.id] = float(producto.precio_unitario)

        respaldo_file = "respaldo_precios.json"
        with open(respaldo_file, "w") as f:
            json.dump(respaldo, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Respaldo de precios creado en '{respaldo_file}'"))

        # -------------------------------
        # Actualizar precios
        # -------------------------------
        for producto in Producto.objects.all():
            precio_anterior = producto.precio_unitario
            producto.precio_unitario = (precio_anterior * Decimal(factor)).quantize(Decimal("1.00"))
            producto.save()
            self.stdout.write(f'Producto "{producto.nombre}": {precio_anterior} -> {producto.precio_unitario}')

        self.stdout.write(self.style.SUCCESS(
            f"Se aumentaron todos los precios en un {porcentaje_aumento}%"
        ))
