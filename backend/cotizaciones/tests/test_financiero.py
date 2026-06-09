from decimal import Decimal

import pytest
from django.db import IntegrityError

from ..models import (
    Cotizacion,
    CotizacionItem,
    Factura,
    ItemFactura,
    Recibo,
    ReciboItem,
    Compra,
    CompraItem,
    Producto,
)


class TestCotizacionCalculos:
    """Tests de cálculos financieros de Cotizaciones"""

    def test_total_sin_items(self, cliente, usuario_admin):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-001",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        assert cotizacion.total == Decimal("0.00")
        assert cotizacion.subtotal_bruto == Decimal("0.00")

    def test_item_calcula_subtotal(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-002",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        item = CotizacionItem.objects.create(
            cotizacion=cotizacion,
            producto=producto,
            cantidad=3,
            precio_unitario=Decimal("150.00"),
        )
        assert item.subtotal == Decimal("450.00")

    def test_total_acumula_items(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-003",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=2, precio_unitario=Decimal("100.00")
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("350.50")
        )
        cotizacion.refresh_from_db()
        assert cotizacion.total == Decimal("550.50")
        assert cotizacion.subtotal_bruto == Decimal("550.50")

    def test_descuento_porcentaje(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-004",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
            descuento_porcentaje=Decimal("10.00"),
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=2, precio_unitario=Decimal("200.00")
        )
        cotizacion.refresh_from_db()
        assert cotizacion.subtotal_bruto == Decimal("400.00")
        assert cotizacion.monto_descuento == Decimal("40.00")
        assert cotizacion.total == Decimal("360.00")

    def test_descuento_cero(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-005",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
            descuento_porcentaje=Decimal("0.00"),
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("100.00")
        )
        cotizacion.refresh_from_db()
        assert cotizacion.total == Decimal("100.00")

    def test_descuento_cien_porciento(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-006",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
            descuento_porcentaje=Decimal("100.00"),
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("100.00")
        )
        cotizacion.refresh_from_db()
        assert cotizacion.total == Decimal("0.00")

    def test_recalculo_al_cambiar_cantidad(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-007",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        item = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=2, precio_unitario=Decimal("100.00")
        )
        item.cantidad = 5
        item.save()
        cotizacion.refresh_from_db()
        assert cotizacion.total == Decimal("500.00")

    def test_recalculo_al_cambiar_precio(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-008",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        item = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=2, precio_unitario=Decimal("100.00")
        )
        item.precio_unitario = Decimal("120.00")
        item.save()
        cotizacion.refresh_from_db()
        assert cotizacion.total == Decimal("240.00")

    def test_recalculo_al_eliminar_item(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-009",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        item1 = CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("300.00")
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("200.00")
        )
        # El delete del modelo no llama a calcular_total automaticamente,
        # la vista se encarga de ello. Simulamos el comportamiento.
        total_sin_item1 = Decimal("200.00")
        item1.delete()
        cotizacion.calcular_total()
        cotizacion.refresh_from_db()
        assert cotizacion.total == total_sin_item1

    def test_calcular_total_devuelve_valor(self, cliente, usuario_admin, producto):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FIN-010",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=producto, cantidad=1, precio_unitario=Decimal("250.00")
        )
        total = cotizacion.calcular_total()
        assert total == Decimal("250.00")


class TestFacturaCalculos:
    """Tests de cálculos financieros de Facturas"""

    def test_factura_total_sin_items(self, cliente, usuario_admin):
        factura = Factura.objects.create(
            cliente=cliente,
            tipo="C",
            punto_venta=1,
            usuario=usuario_admin,
        )
        assert factura.total == Decimal("0.00")

    def test_factura_acumula_items(self, cliente, usuario_admin):
        factura = Factura.objects.create(
            cliente=cliente,
            tipo="C",
            punto_venta=1,
            usuario=usuario_admin,
        )
        ItemFactura.objects.create(
            factura=factura,
            descripcion="Item 1",
            cantidad=2,
            precio_unit=Decimal("100.00"),
            subtotal=Decimal("200.00"),
        )
        ItemFactura.objects.create(
            factura=factura,
            descripcion="Item 2",
            cantidad=1,
            precio_unit=Decimal("350.50"),
            subtotal=Decimal("350.50"),
        )
        factura.actualizar_totales()
        assert factura.total == Decimal("550.50")

    def test_factura_neto_y_total(self, cliente, usuario_admin):
        factura = Factura.objects.create(
            cliente=cliente,
            tipo="C",
            punto_venta=1,
            usuario=usuario_admin,
        )
        ItemFactura.objects.create(
            factura=factura,
            descripcion="Producto",
            cantidad=1,
            precio_unit=Decimal("1000.00"),
            subtotal=Decimal("1000.00"),
        )
        factura.actualizar_totales()
        assert factura.neto == Decimal("1000.00")
        assert factura.total == Decimal("1000.00")


class TestReciboCalculos:
    """Tests de cálculos financieros de Recibos"""

    def test_recibo_total_cero_sin_items(self, cliente, usuario_admin):
        recibo = Recibo.objects.create(
            numero="REC-TEST-001",
            cliente=cliente,
            fecha="2025-01-01",
            forma_pago="efectivo",
            usuario=usuario_admin,
        )
        assert recibo.total == Decimal("0.00")

    def test_recibo_suma_items(self, cliente, usuario_admin, producto):
        recibo = Recibo.objects.create(
            numero="REC-TEST-002",
            cliente=cliente,
            fecha="2025-01-01",
            forma_pago="transferencia",
            usuario=usuario_admin,
        )
        ReciboItem.objects.create(
            recibo=recibo,
            producto=producto,
            cantidad=2,
            precio_unitario=Decimal("500.00"),
        )
        ReciboItem.objects.create(
            recibo=recibo,
            producto=producto,
            cantidad=1,
            precio_unitario=Decimal("1000.00"),
        )
        recibo.actualizar_totales()
        assert recibo.total == Decimal("2000.00")


class TestCompraCalculos:
    """Tests de cálculos financieros de Compras"""

    def test_compra_total_cero_sin_items(self, proveedor, usuario_admin):
        compra = Compra.objects.create(
            numero="COMP-TEST-001",
            proveedor=proveedor,
            fecha="2025-01-01",
            usuario=usuario_admin,
        )
        assert compra.total == Decimal("0.00")

    def test_compra_suma_items(self, proveedor, usuario_admin, producto):
        compra = Compra.objects.create(
            numero="COMP-TEST-002",
            proveedor=proveedor,
            fecha="2025-01-01",
            usuario=usuario_admin,
        )
        CompraItem.objects.create(
            compra=compra,
            producto=producto,
            cantidad=10,
            precio_unitario=Decimal("50.00"),
        )
        compra.actualizar_totales()
        compra.refresh_from_db()
        assert compra.total == Decimal("500.00")


class TestUniqueConstraints:
    """Tests de restricciones de unicidad"""

    def test_cotizacion_numero_unico(self, cliente, usuario_admin):
        Cotizacion.objects.create(
            numero="UNICO-001",
            cliente=cliente,
            tipo_documento="presupuesto",
            usuario=usuario_admin,
        )
        with pytest.raises(IntegrityError):
            Cotizacion.objects.create(
                numero="UNICO-001",
                cliente=cliente,
                tipo_documento="presupuesto",
                usuario=usuario_admin,
            )

    def test_recibo_numero_unico(self, cliente, usuario_admin):
        Recibo.objects.create(
            numero="REC-UNICO-001",
            cliente=cliente,
            fecha="2025-01-01",
            forma_pago="efectivo",
            usuario=usuario_admin,
        )
        with pytest.raises(IntegrityError):
            Recibo.objects.create(
                numero="REC-UNICO-001",
                cliente=cliente,
                fecha="2025-01-01",
                forma_pago="efectivo",
                usuario=usuario_admin,
            )
