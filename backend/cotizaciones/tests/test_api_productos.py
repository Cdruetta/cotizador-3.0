from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Proveedor, Producto


class ProductosAPITestCase(APITestCase):

    def setUp(self):
        # 👤 1. Roles de usuario para la API
        self.usuario_comun = User.objects.create_user(
            username="empleado_prod", 
            email="empleado_prod@gcinsumos.com", 
            password="ProdPassword123"
        )
        
        self.usuario_admin = User.objects.create_user(
            username="admin_prod", 
            email="admin_prod@gcinsumos.com", 
            password="AdminProdPassword123",
            is_staff=True
        )

        # 📦 2. Datos de base requeridos (Un producto necesita un proveedor)
        self.proveedor = Proveedor.objects.create(
            nombre="Mayorista Tecnológico S.A.",
            contacto="Juan Pérez",
            telefono="3584001122"
        )

        self.producto = Producto.objects.create(
            nombre="Disco Sólido SSD 480GB Kingston",
            descripcion="SSD SATA3 de alta velocidad",
            precio_unitario=Decimal("45000.00"),
            proveedor=self.proveedor
        )

        # 🎯 Endpoints fijos de la API v3 para Productos
        self.url_listado_productos = '/api/v3/productos/'
        self.url_detalle_producto = f'/api/v3/productos/{self.producto.pk}/'

    def autenticar_usuario(self, usuario):
        """Inyecta de forma dinámica las credenciales JWT del usuario en el cliente de pruebas"""
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # ==========================================
    # 🔒 CAPA 1: SEGURIDAD Y JWT
    # ==========================================
    def test_productos_denegado_sin_token(self):
        """Un usuario sin autenticar debe recibir 401 al intentar listar productos"""
        self.client.credentials()  # Limpieza de cabeceras
        response = self.client.get(self.url_listado_productos)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================================
    # 🛡️ CAPA 2: PERMISOS POR ROL (Empleado Común)
    # ==========================================
    def test_empleado_puede_listar_productos(self):
        """Cualquier empleado autenticado puede consultar el catálogo de productos (200 OK)"""
        self.autenticar_usuario(self.usuario_comun)
        response = self.client.get(self.url_listado_productos)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Validamos que devuelva al menos el producto que creamos en el setUp
        self.assertContains(response, "Disco Sólido SSD 480GB Kingston")

    def test_empleado_no_puede_crear_producto(self):
        """Un empleado común tiene prohibido dar de alta productos (403 Forbidden)"""
        self.autenticar_usuario(self.usuario_comun)
        nuevo_prod = {
            "nombre": "Memoria RAM 16GB DDR4",
            "precio_unitario": "62000.00",
            "proveedor": self.proveedor.pk
        }
        response = self.client.post(self.url_listado_productos, nuevo_prod, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empleado_no_puede_eliminar_producto(self):
        """Un empleado común no puede borrar un producto del catálogo (403 Forbidden)"""
        self.autenticar_usuario(self.usuario_comun)
        response = self.client.delete(self.url_detalle_producto)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================
    # 🚀 CAPA 3: FLUJO CRUD COMPLETO (Admin / Staff)
    # ==========================================
    def test_admin_puede_crear_producto_valido(self):
        """El administrador puede registrar nuevos productos de forma exitosa (201 Created)"""
        self.autenticar_usuario(self.usuario_admin)
        data = {
            "nombre": "Gabinete Kit Sentey",
            "descripcion": "Incluye fuente de 500W, teclado y mouse",
            "precio_unitario": "38000.00",
            "proveedor": self.proveedor.pk
        }
        response = self.client.post(self.url_listado_productos, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Producto.objects.filter(nombre="Gabinete Kit Sentey").exists())

    def test_admin_puede_actualizar_precio_producto(self):
        """El administrador puede remarcar precios o modificar datos del producto (200 OK)"""
        self.autenticar_usuario(self.usuario_admin)
        data_actualizada = {
            "nombre": "Disco Sólido SSD 480GB Kingston",
            "precio_unitario": "49999.99",  # Ajuste de precio por inflación/cambio
            "proveedor": self.proveedor.pk
        }
        response = self.client.put(self.url_detalle_producto, data_actualizada, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validamos impacto real en base de datos
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.precio_unitario, Decimal("49999.99"))

    def test_admin_puede_eliminar_producto(self):
        """El administrador puede quitar un producto del catálogo si es necesario (204 No Content)"""
        self.autenticar_usuario(self.usuario_admin)
        response = self.client.delete(self.url_detalle_producto)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())