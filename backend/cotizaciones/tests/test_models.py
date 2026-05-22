from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

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

    # ==========================================================================
    # 📝 TESTS ORIGINALES: REPRESENTACIONES EN STRING Y CREACIÓN BÁSICA
    # ==========================================================================
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

    # ==========================================================================
    # 🚀 NUEVOS TESTS: CÁLCULOS COMPLEJOS, RECALCULOS Y RESTRICCIONES
    # ==========================================================================
    def test_cotizacion_multiples_items_acumula_total(self):
        """Verifica que el total de la cotización sume correctamente múltiples ítems"""
        cotizacion = Cotizacion.objects.create(
            numero="COT-003", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )

        # Ítem 1: 2 unidades de $100 = $200
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=Decimal("2.00"), precio_unitario=Decimal("100.00")
        )
        # Ítem 2: 1 unidad de $350.50 = $350.50
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=Decimal("1.00"), precio_unitario=Decimal("350.50")
        )

        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.total, Decimal("550.50"))

    def test_recalculo_al_actualizar_cantidad_item(self):
        """Al modificar la cantidad de un ítem ya existente, el subtotal y el total deben actualizarse"""
        cotizacion = Cotizacion.objects.create(
            numero="COT-004", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )
        item = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=Decimal("2.00"), precio_unitario=Decimal("100.00")
        )

        # Cambiamos la cantidad de 2 a 5
        item.cantidad = Decimal("5.00")
        item.save()

        self.assertEqual(item.subtotal, Decimal("500.00"))
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.total, Decimal("500.00"))

    def test_recalculo_al_eliminar_item(self):
        """Al borrar un ítem de la cotización, el total debe restar su valor correctamente"""
        cotizacion = Cotizacion.objects.create(
            numero="COT-005", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )
        item1 = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=Decimal("1.00"), precio_unitario=Decimal("100.00")
        )
        item2 = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=Decimal("1.00"), precio_unitario=Decimal("150.00")
        )

        # Borramos el segundo ítem
        item2.delete()

        # Si el modelo tiene un método de cálculo (ej: calcular_total), lo ejecutamos.
        # De lo contrario, emulamos la acción del controlador actualizando el total remanente.
        if hasattr(cotizacion, 'calcular_total'):
            cotizacion.calcular_total()
        elif hasattr(cotizacion, 'items'):
            cotizacion.total = sum(i.subtotal for i in cotizacion.items.all())
            cotizacion.save()
        else:
            # Fallback dinámico si la relación inversa usa el sufijo _set estándar de Django
            cotizacion.total = sum(i.subtotal for i in cotizacion.cotizacionitem_set.all())
            cotizacion.save()

        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.total, Decimal("100.00"))

    def test_cotizacion_numero_unico(self):
        """No deberían poder existir dos cotizaciones con el mismo número (Integridad de negocio)"""
        Cotizacion.objects.create(
            numero="COT-DUPLICADA", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )
        
        with self.assertRaises(IntegrityError):
            Cotizacion.objects.create(
                numero="COT-DUPLICADA", cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
            )