from decimal import Decimal
from django.core.management.base import BaseCommand
from cotizaciones.models import Producto

class Command(BaseCommand):
    help = "Aumenta el precio de todos los productos un porcentaje dado"

    def add_arguments(self, parser):
        parser.add_argument(
            '--porcentaje',
            type=float,
            default=10.0, #<--- cambiar aca el valor del aumento en porcentaje
            help='Porcentaje de aumento de precios (por defecto 10%)'
        )

    def handle(self, *args, **options):
        porcentaje = options['porcentaje']
        factor = 1 + (porcentaje / 100)

        productos = Producto.objects.all()
        for producto in productos:
            precio_anterior = producto.precio_unitario
            producto.precio_unitario = (precio_anterior * Decimal(factor)).quantize(Decimal('1.00'))
            producto.save()
            self.stdout.write(
                f'Producto "{producto.nombre}" actualizado: {precio_anterior} -> {producto.precio_unitario}'
            )

        self.stdout.write(self.style.SUCCESS(f"Se aumentaron todos los precios en un {porcentaje}%"))
