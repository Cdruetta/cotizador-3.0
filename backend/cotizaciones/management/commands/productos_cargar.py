import os
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from cotizaciones.models import Producto, Proveedor


class Command(BaseCommand):
    help = "Crea superusuario (si se configura) y carga productos iniciales en la DB."

    def handle(self, *args, **kwargs):
        user_model = get_user_model()
        username = os.environ.get("BOOTSTRAP_SUPERUSER_USERNAME")
        email = os.environ.get("BOOTSTRAP_SUPERUSER_EMAIL")
        password = os.environ.get("BOOTSTRAP_SUPERUSER_PASSWORD")

        if username and email and password:
            if not user_model.objects.filter(username=username).exists():
                user_model.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado.'))
            else:
                self.stdout.write(self.style.WARNING(f'Superusuario "{username}" ya existe.'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Superusuario no configurado: faltan BOOTSTRAP_SUPERUSER_USERNAME/EMAIL/PASSWORD."
                )
            )

        proveedores = ["Proveedor Default", "GCsoft", "GCinsumos", "Good Game", "Mercado Libre", "David Re"]
        for nombre in proveedores:
            Proveedor.objects.get_or_create(nombre=nombre)

        proveedor_default = Proveedor.objects.get(nombre="Proveedor Default")

        productos = [
            ("DIAGNÓSTICOS", "Diagnóstico - 20% del valor de la mano de obra presupuestada", "13800"),
            ("SOFTWARE", "Inicialización equipo nuevo (programas básicos)", "28300"),
            ("SOFTWARE", "Inicialización equipo nuevo (programas básicos y Windows)", "46750"),
            ("SOFTWARE", "Formateo + Instalación prog. básicos + Backup hasta 100Gb", "55200"),
            ("SOFTWARE", "Backup de datos: cada 250Gb extras", "12750"),
            ("SOFTWARE", "Backup en más de una unidad", "12750"),
            ("SOFTWARE", "Mantenimiento y limpieza de virus y optimización", "37700"),
            ("SOFTWARE", "Instalación de un solo programa", "17800"),
            ("SOFTWARE", "Pack por tres programas", "27950"),
            ("SOFTWARE", "Programa extra al pack", "10600"),
            ("HARDWARE", "Armado de PC común (solo armado)", "19300"),
            ("HARDWARE", "Armado de PC Gamer (solo armado)", "36200"),
            ("HARDWARE", "Mantenimiento de hardware notebook", "54400"),
            ("HARDWARE", "Mantenimiento de hardware PC común", "31050"),
            ("HARDWARE", "Mantenimiento de hardware PC Gamer", "84750"),
            ("HARDWARE", "Instalación de hardware notebook", "28300"),
            ("HARDWARE", "Instalación de hardware PC común", "16350"),
            ("HARDWARE", "Instalación de hardware PC Gamer", "35900"),
            ("HARDWARE", "Reparación de bisagras de notebook", "71750"),
            ("HARDWARE", "Reparación de pin de carga o botones notebook", "71750"),
            ("HARDWARE", "Cambio de teclado de notebook", "19300"),
            ("HARDWARE", "Cambio de teclado de notebook (Equipos complejos)", "36200"),
            ("HARDWARE", "Cambio de pantalla de notebook", "43350"),
            ("IMPRESORAS", "InkJet simple función", "24700"),
            ("IMPRESORAS", "Hp Inkjet multifunción común", "34600"),
            ("IMPRESORAS", "Epson chorro de tinta series CX-TX", "48300"),
            ("IMPRESORAS", "Epson chorro de tinta series XP", "38650"),
            ("IMPRESORAS", "Destapado de cabezal", "54950"),
            ("IMPRESORAS", "Serie L A4 - Destapado de cabezal", "65900"),
            ("IMPRESORAS", "Serie L A4 - Mantenimiento y limpieza", "65900"),
            ("IMPRESORAS", "Serie L A4 - Destapado + Mantenimiento", "110400"),
            ("IMPRESORAS", "Serie Fotográfico A4 - Destapado de cabezal", "85400"),
            ("IMPRESORAS", "Serie Fotográfico A4 - Mantenimiento y limpieza", "85400"),
            ("IMPRESORAS", "Serie Fotográfico A4 - Destapado + Mantenimiento", "143050"),
            ("IMPRESORAS", "Impresoras A3 - Destapado de cabezal", "130300"),
            ("IMPRESORAS", "Impresoras A3 - Mantenimiento y limpieza", "145950"),
            ("IMPRESORAS", "Impresoras A3 - Destapado + Mantenimiento", "259300"),
            ("IMPRESORAS", "Impresora Láser A4 simple función", "47450"),
            ("IMPRESORAS", "Impresora Láser gran formato o multifunción", "85000"),
            ("IMPRESORAS", "Matriz de punto", "47450"),
            ("OTROS", "Descarga externa", "19100"),
            ("OTROS", "Desbloqueo de contadores", "28150"),
            ("OTROS", "Descarga externa + desbloqueo", "36800"),
            ("OTROS", "Atención remota (por cada media hora)", "19000"),
            ("OTROS", "Atención en domicilio (por cada media hora) hasta 3Km", "24050"),
            ("OTROS", "Atención en domicilio (extra por km)", "3450"),
            ("OTROS", "Cambio de cable cargador", "12050"),
            ("REDES", "Atención en domicilio (por cada media hora) hasta 3Km", "24400"),
            ("REDES", "Instalación de routers y otros", "30450"),
            ("REDES", "Extra por cada dispositivo", "10050"),
            ("REPARACIONES", "Reparación de placa / reballing - 20% del valor del equipo", "167100"),
        ]

        for _, desc, precio in productos:
            Producto.objects.get_or_create(
                nombre=desc,
                defaults={
                    "precio_unitario": Decimal(precio.replace("$", "").replace(",", "")),
                    "activo": True,
                    "proveedor": proveedor_default,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"{len(productos)} productos creados exitosamente."))

