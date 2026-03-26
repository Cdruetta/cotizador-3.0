from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123", email="test@example.com")

        self.cliente = Cliente.objects.create(
            nombre="Cliente Test",
            direccion="Dirección Test",
            telefono="123456789",
            localidad="Ciudad Test",
            email="cliente@test.com",
        )

        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor Test",
            contacto="Contacto Test",
            telefono="987654321",
            email="proveedor@test.com",
        )

        self.producto = Producto.objects.create(
            nombre="Producto Test",
            descripcion="Descripción del producto test",
            precio_unitario=Decimal("100.00"),
            proveedor=self.proveedor,
        )

    def test_cliente_str(self):
        self.assertEqual(str(self.cliente), "Cliente Test")

    def test_proveedor_str(self):
        self.assertEqual(str(self.proveedor), "Proveedor Test")

    def test_producto_str(self):
        self.assertEqual(str(self.producto), "Producto Test")

    def test_cotizacion_creation(self):
        cotizacion = Cotizacion.objects.create(
            numero="COT-001", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )
        self.assertEqual(str(cotizacion), "COT-001 - Cliente Test")

    def test_cotizacion_item_calculation(self):
        cotizacion = Cotizacion.objects.create(
            numero="COT-002", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )

        item = CotizacionItem.objects.create(
            cotizacion=cotizacion,
            producto=self.producto,
            cantidad=Decimal("2.00"),
            precio_unitario=Decimal("100.00"),
        )

        self.assertEqual(item.subtotal, Decimal("200.00"))
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.total, Decimal("200.00"))

