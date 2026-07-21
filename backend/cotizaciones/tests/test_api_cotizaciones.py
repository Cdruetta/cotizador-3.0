from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Cliente, Cotizacion, Producto, Proveedor


class CotizacionesAPITestCase(APITestCase):

    def setUp(self):
        # 1. Usuarios y Roles
        self.usuario_comun = User.objects.create_user(
            username="empleado_coti", 
            email="empleado_coti@gcinsumos.com", 
            password="CotiPassword123"
        )
        self.usuario_admin = User.objects.create_user(
            username="admin_coti", 
            email="admin_coti@gcinsumos.com", 
            password="AdminCotiPassword123",
            is_staff=True
        )

        # 2. Entidades requeridas para relacionar una cotizaciÃ³n
        self.cliente = Cliente.objects.create(
            nombre="ComputaciÃ³n RÃ­o Cuarto",
            telefono="3584112233"
        )
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor Base",
            telefono="111"
        )
        self.producto = Producto.objects.create(
            nombre="Monitor 24 IPS",
            precio_unitario=Decimal("120000.00"),
            proveedor=self.proveedor
        )

        # 3. Creamos una cotizaciÃ³n base asociada al admin
        self.cotizacion = Cotizacion.objects.create(
            numero="COT-API-001",
            cliente=self.cliente,
            tipo_documento="presupuesto",
            usuario=self.usuario_admin
        )

        # Endpoints v3 para Cotizaciones
        self.url_listado_cotizaciones = '/api/v3/cotizaciones/'
        self.url_detalle_cotizacion = f'/api/v3/cotizaciones/{self.cotizacion.pk}/'

    def autenticar_usuario(self, usuario):
        """Inyecta credenciales JWT para las llamadas de prueba"""
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # ==========================================
    # SEGURIDAD & ACCESOS
    # ==========================================
    def test_cotizaciones_denegado_sin_token(self):
        """Bloqueo inmediato a usuarios anÃ³nimos (401 Unauthorized)"""
        self.client.credentials()
        response = self.client.get(self.url_listado_cotizaciones)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empleado_puede_listar_cotizaciones(self):
        """Los empleados pueden auditar y ver los presupuestos del sistema (200 OK)"""
        self.autenticar_usuario(self.usuario_comun)
        response = self.client.get(self.url_listado_cotizaciones)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "COT-API-001")

    # ==========================================
    # OPERACIONES CRUD (Admin / Personal Autorizado)
    # ==========================================
    def test_admin_puede_crear_cotizacion_vacia(self):
        """Verifica la cabecera inicial de una cotizaciÃ³n vinculada al cliente (201 Created)"""
        self.autenticar_usuario(self.usuario_admin)
        data = {
            "numero": "COT-API-002",
            "cliente": self.cliente.pk,
            "tipo_documento": "presupuesto",
            "usuario": self.usuario_admin.id
        }
        response = self.client.post(self.url_listado_cotizaciones, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cotizacion.objects.filter(numero="COT-API-002").exists())

    def test_cotizacion_no_encontrada_devuelve_404(self):
        """Buscar un ID de presupuesto inexistente debe responder con un 404 limpio"""
        self.autenticar_usuario(self.usuario_admin)
        url_invalida = '/api/v3/cotizaciones/999999/'
        response = self.client.get(url_invalida)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_puede_eliminar_cotizacion(self):
        """Un administrador puede purgar o dar de baja una cotizaciÃ³n (204 No Content)"""
        self.autenticar_usuario(self.usuario_admin)
        response = self.client.delete(self.url_detalle_cotizacion)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cotizacion.objects.filter(pk=self.cotizacion.pk).exists())
