from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Cliente, Factura, ItemFactura, Proveedor, Producto


@pytest.mark.django_db
class TestFacturasAPI:
    """Tests de la API REST de Facturas (/api/v3/facturas/)"""

    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_fac", password="pass1234", is_staff=True, is_superuser=True
        )
        self.user = User.objects.create_user(
            username="user_fac", password="pass1234"
        )
        self.cliente = Cliente.objects.create(nombre="Cliente Factura")
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.url = "/api/v3/facturas/"

    def test_listar_facturas(self):
        Factura.objects.create(cliente=self.cliente, tipo="C", punto_venta=1, usuario=self.admin)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_crear_factura(self):
        data = {
            "cliente": self.cliente.pk,
            "tipo": "C",
            "punto_venta": 1,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["estado"] == "borrador"

    def test_crear_factura_sin_cliente(self):
        data = {"tipo": "C", "punto_venta": 1}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_detalle_factura(self):
        factura = Factura.objects.create(cliente=self.cliente, tipo="C", punto_venta=1, usuario=self.admin)
        response = self.client.get(f"{self.url}{factura.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["cliente"] == self.cliente.pk

    def test_eliminar_factura(self):
        factura = Factura.objects.create(cliente=self.cliente, tipo="C", punto_venta=1, usuario=self.admin)
        response = self.client.delete(f"{self.url}{factura.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_factura_no_encontrada(self):
        response = self.client.get(f"{self.url}99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_usuario_no_autorizado(self):
        self.client.credentials()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestFiltrosAPI:
    """Tests de filtros en endpoints de la API"""

    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_filtros", password="pass1234", is_staff=True
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_filtrar_productos_por_tipo(self):
        proveedor = Proveedor.objects.create(nombre="Prov")
        Producto.objects.create(nombre="Producto A", tipo="producto", proveedor=proveedor)
        Producto.objects.create(nombre="Servicio A", tipo="servicio_soft", proveedor=proveedor)
        response = self.client.get("/api/v3/productos/", {"tipo": "producto"})
        assert response.status_code == 200
        data = response.json()
        for p in data:
            assert p["tipo"] == "producto"

    def test_filtrar_clientes_por_search(self):
        Cliente.objects.create(nombre="Juan Perez")
        Cliente.objects.create(nombre="Maria Gomez")
        response = self.client.get("/api/v3/clientes/", {"search": "Juan"})
        assert response.status_code == 200
        names = [c["nombre"] for c in response.json()]
        assert "Juan Perez" in names
        assert "Maria Gomez" not in names

    def test_filtrar_cotizaciones_por_estado(self, cotizacion_data):
        from ..models import Cotizacion
        Cotizacion.objects.create(
            numero="COT-FILTRO-001",
            cliente_id=cotizacion_data["cliente"],
            tipo_documento="presupuesto",
            usuario_id=cotizacion_data["usuario"],
            estado="borrador",
        )
        Cotizacion.objects.create(
            numero="COT-FILTRO-002",
            cliente_id=cotizacion_data["cliente"],
            tipo_documento="presupuesto",
            usuario_id=cotizacion_data["usuario"],
            estado="aprobada",
        )
        response = self.client.get("/api/v3/cotizaciones/", {"estado": "aprobada"})
        assert response.status_code == 200
        for c in response.json():
            assert c["estado"] == "aprobada"
