from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

from ..models import (
    Cliente,
    Proveedor,
    Producto,
    Cotizacion,
    CotizacionItem,
    Factura,
    Recibo,
    Categoria,
    Marca,
)


@pytest.mark.django_db
class TestDashboardViews:
    """Tests de las vistas principales del dashboard"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")

    def test_login_required(self):
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_dashboard_con_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 200
        assert "Dashboard" in response.content.decode()

    def test_reportes_con_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reportes"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestClienteViews:
    """Tests CRUD de clientes via web"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.client.force_login(self.user)

    def test_lista_clientes(self):
        Cliente.objects.create(nombre="Cliente A")
        response = self.client.get(reverse("cliente_list"))
        assert response.status_code == 200
        assert "Cliente A" in response.content.decode()

    def test_crear_cliente(self):
        response = self.client.post(
            reverse("cliente_create"),
            {"nombre": "Nuevo Cliente", "telefono": "123456789", "email": "nuevo@test.com"},
        )
        assert response.status_code == 302
        assert Cliente.objects.filter(nombre="Nuevo Cliente").exists()

    def test_editar_cliente(self):
        cliente = Cliente.objects.create(nombre="Original")
        response = self.client.post(
            reverse("cliente_update", args=[cliente.pk]),
            {"nombre": "Modificado", "telefono": "", "email": ""},
        )
        assert response.status_code == 302
        cliente.refresh_from_db()
        assert cliente.nombre == "Modificado"

    def test_eliminar_cliente(self):
        cliente = Cliente.objects.create(nombre="A eliminar")
        response = self.client.post(reverse("cliente_delete", args=[cliente.pk]))
        assert response.status_code == 302
        assert not Cliente.objects.filter(pk=cliente.pk).exists()

    def test_detalle_cliente(self):
        cliente = Cliente.objects.create(nombre="Detalle", telefono="123")
        response = self.client.get(reverse("cliente_detail", args=[cliente.pk]))
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductoViews:
    """Tests CRUD de productos via web"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.client.force_login(self.user)
        self.proveedor = Proveedor.objects.create(nombre="Prov Test")

    def test_crear_producto(self):
        response = self.client.post(
            reverse("producto_create"),
            {
                "nombre": "Producto Nuevo",
                "tipo": "producto",
                "precio_unitario": "150.00",
                "proveedor": self.proveedor.pk,
                "stock": 0,
                "activo": True,
            },
        )
        assert response.status_code == 302
        assert Producto.objects.filter(nombre="Producto Nuevo").exists()

    def test_lista_productos_muestra_nombre(self):
        Producto.objects.create(nombre="Monitor LG", proveedor=self.proveedor, precio_unitario=Decimal("500.00"), tipo="producto")
        response = self.client.get(reverse("producto_list"))
        assert response.status_code == 200
        assert "Monitor LG" in response.content.decode()

    def test_producto_detail(self):
        p = Producto.objects.create(nombre="Teclado", proveedor=self.proveedor, precio_unitario=Decimal("50.00"), tipo="producto")
        response = self.client.get(reverse("producto_detail", args=[p.pk]))
        assert response.status_code == 200


@pytest.mark.django_db
class TestCotizacionFlow:
    """Tests del flujo completo de cotizaciÃ³n (crear + items)"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.client.force_login(self.user)
        self.cliente = Cliente.objects.create(nombre="Cliente Cotizacion")
        self.proveedor = Proveedor.objects.create(nombre="Prov")
        self.producto = Producto.objects.create(
            nombre="Producto Cot",
            proveedor=self.proveedor,
            precio_unitario=Decimal("100.00"),
            tipo="producto",
        )

    def test_crear_cotizacion(self):
        response = self.client.post(
            reverse("cotizacion_create"),
            {"cliente": self.cliente.pk, "tipo_documento": "presupuesto"},
        )
        assert response.status_code == 302
        cotizacion = Cotizacion.objects.filter(cliente=self.cliente).first()
        assert cotizacion is not None

    def test_cotizacion_detalle_muestra_items(self):
        cotizacion = Cotizacion.objects.create(
            cliente=self.cliente, tipo_documento="presupuesto", usuario=self.user
        )
        CotizacionItem.objects.create(
            cotizacion=cotizacion, producto=self.producto, cantidad=2, precio_unitario=Decimal("100.00")
        )
        response = self.client.get(reverse("cotizacion_detail", args=[cotizacion.pk]))
        assert response.status_code == 200
        assert "Producto Cot" in response.content.decode()

    def test_cambio_estado_cotizacion(self):
        cotizacion = Cotizacion.objects.create(
            numero="COT-FLOW-001",
            cliente=self.cliente,
            tipo_documento="presupuesto",
            usuario=self.user,
            estado="borrador",
        )
        response = self.client.post(
            reverse("cambiar_estado_cotizacion", args=[cotizacion.pk, "aprobada"])
        )
        assert response.status_code == 302
        cotizacion.refresh_from_db()
        assert cotizacion.estado == "aprobada"

    def test_cotizacion_pdf(self):
        cotizacion = Cotizacion.objects.create(
            numero="COT-PDF-001",
            cliente=self.cliente,
            tipo_documento="presupuesto",
            usuario=self.user,
        )
        fake_response = HttpResponse(content_type="application/pdf")
        with patch(
            "cotizaciones.views.cotizaciones.build_cotizacion_pdf_response",
            return_value=fake_response,
        ):
            response = self.client.get(reverse("generar_pdf", args=[cotizacion.pk]))
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"


@pytest.mark.django_db
class TestReciboFlow:
    """Tests del flujo de recibos"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.client.force_login(self.user)
        self.cliente = Cliente.objects.create(nombre="Cliente Recibo")

    def test_crear_recibo(self):
        response = self.client.post(
            reverse("recibo_create"),
            {
                "cliente": self.cliente.pk,
                "fecha": "2025-01-15",
                "forma_pago": "efectivo",
                "total": "1000.00",
            },
        )
        assert response.status_code == 302

    def test_recibo_pdf(self):
        recibo = Recibo.objects.create(
            numero="REC-PDF-001",
            cliente=self.cliente,
            fecha="2025-01-15",
            forma_pago="efectivo",
            usuario=self.user,
        )
        response = self.client.get(reverse("recibo_pdf", args=[recibo.pk]))
        assert response.status_code == 200


@pytest.mark.django_db
class TestCategoriaMarcaViews:
    """Tests de categorÃ­as y marcas"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass1234")
        self.client.force_login(self.user)

    def test_crear_categoria(self):
        response = self.client.post(
            reverse("categoria_create"), {"nombre": "Nueva Cat", "activo": True}
        )
        assert response.status_code == 302
        assert Categoria.objects.filter(nombre="Nueva Cat").exists()

    def test_crear_marca(self):
        response = self.client.post(
            reverse("marca_create"), {"nombre": "Nueva Marca", "activo": True}
        )
        assert response.status_code == 302
        assert Marca.objects.filter(nombre="Nueva Marca").exists()

    def test_categoria_unique(self):
        Categoria.objects.create(nombre="Unica")
        response = self.client.post(
            reverse("categoria_create"), {"nombre": "Unica", "activo": True}
        )
        assert response.status_code == 200  # Se queda en la misma pÃ¡gina (error de formulario)
        assert Categoria.objects.filter(nombre="Unica").count() == 1


@pytest.mark.django_db
class TestPermisos:
    """Tests de permisos de vistas web"""

    def test_cliente_list_requiere_login(self):
        client = Client()
        response = client.get(reverse("cliente_list"))
        assert response.status_code == 302

    def test_login_redirige_al_dashboard(self):
        user = User.objects.create_user(username="test", password="pass1234")
        client = Client()
        client.force_login(user)
        response = client.get(reverse("cliente_list"))
        assert response.status_code == 200

    def test_logout_cierra_sesion(self):
        client = Client()
        user = User.objects.create_user(username="test", password="pass1234")
        client.force_login(user)
        response = client.post(reverse("logout"), follow=True)
        assert response.status_code == 200


@pytest.mark.django_db
class TestConfigViews:
    """Tests de vistas de configuraciÃ³n"""

    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(username="admin", password="pass1234", is_staff=True)
        self.client.force_login(self.user)

    def test_configuracion_view(self):
        response = self.client.get(reverse("configuracion"))
        assert response.status_code == 200

    def test_configuracion_afip_view(self):
        response = self.client.get(reverse("facturacion_config"))
        assert response.status_code == 200
