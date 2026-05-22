from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Cliente


# ==========================================================================
# 🏠 VISTAS WEB TRADICIONALES (Tus tests originales intactos)
# ==========================================================================
class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.cliente = Cliente.objects.create(nombre="Cliente Test", telefono="123456789")

    def test_login_required(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/login/?next=/")

    def test_dashboard_view(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_cliente_list_view(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("cliente_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente Test")

    def test_cliente_create_view(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("cliente_create"),
            {"nombre": "Nuevo Cliente", "telefono": "555-1234", "email": "nuevo@cliente.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cliente.objects.filter(nombre="Nuevo Cliente").exists())


# ==========================================================================
# 🛡️ SUITE DE API V3: VALIDACIÓN JWT, ROLES Y CRUD INTEGRADO EXTENDIDO
# ==========================================================================
class CotizadorAPITestCase(APITestCase):

    def setUp(self):
        # 👤 1. Usuario común (Solo lectura en la API)
        self.usuario_comun = User.objects.create_user(
            username="empleado_api", 
            email="empleado_api@gcinsumos.com", 
            password="PasswordSecure123"
        )
        
        # 👑 2. Usuario Administrador (Control total / Personal de Staff)
        self.usuario_admin = User.objects.create_user(
            username="admin_api", 
            email="admin_api@gcinsumos.com", 
            password="AdminSecure123",
            is_staff=True
        )

        # 📦 3. Entidad de prueba adaptada a tus campos reales ('nombre', 'telefono')
        self.cliente_api = Cliente.objects.create(
            nombre="Insumos Tecnológicos S.A.",
            telefono="3584112233"
        )

        # 🎯 Paths fijos de la API v3
        self.url_listado_clientes = '/api/v3/clientes/'
        self.url_detalle_cliente = f'/api/v3/clientes/{self.cliente_api.pk}/'

    def autenticar_cliente(self, usuario):
        """Genera tokens JWT dinámicos e inyecta la cabecera usando el método nativo de DRF"""
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # ==========================================
    # 🔒 CAPA 1: VALIDACIÓN JWT & SEGURIDAD
    # ==========================================
    def test_acceso_denegado_sin_token(self):
        """Verifica que un usuario anónimo sin token reciba 401 Unauthorized"""
        self.client.credentials()  
        response = self.client.get(self.url_listado_clientes)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================================
    # 🛡️ CAPA 2: RESTRICCIÓN DE ROLES
    # ==========================================
    def test_usuario_comun_puede_leer_pero_no_crear(self):
        """Un usuario normal puede listar (200 OK) pero no puede hacer POST (403 Forbidden)"""
        self.autenticar_cliente(self.usuario_comun)
        
        response_get = self.client.get(self.url_listado_clientes)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        nuevo_cliente = {"nombre": "Intento Fallido SRL", "telefono": "111222333"}
        response_post = self.client.post(self.url_listado_clientes, nuevo_cliente, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_comun_no_puede_eliminar(self):
        """Un usuario normal recibe 403 Forbidden si intenta mandar un DELETE"""
        self.autenticar_cliente(self.usuario_comun)
        response = self.client.delete(self.url_detalle_cliente)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_comun_no_puede_actualizar(self):
        """Un usuario normal recibe 403 Forbidden si intenta mandar un PUT para modificar un cliente"""
        self.autenticar_cliente(self.usuario_comun)
        data_actualizada = {"nombre": "Hackeo Nombre", "telefono": "999999"}
        response = self.client.put(self.url_detalle_cliente, data_actualizada, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================
    # 🚀 CAPA 3: FLUJO CRUD COMPLETO & ERRORES (Admin)
    # ==========================================
    def test_administrador_puede_crear_cliente(self):
        """Un usuario staff (admin) puede registrar datos mediante POST (201 Created)"""
        self.autenticar_cliente(self.usuario_admin)
        data = {
            "nombre": "Nuevos Horizontes Computación",
            "telefono": "3584999999"
        }
        response = self.client.post(self.url_listado_clientes, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cliente.objects.filter(nombre="Nuevos Horizontes Computación").exists())

    def test_creacion_cliente_datos_invalidos(self):
        """El administrador recibe un 400 Bad Request si intenta enviar datos vacíos o incorrectos"""
        self.autenticar_cliente(self.usuario_admin)
        data_invalida = {"nombre": "", "telefono": ""}  # Asumiendo que 'nombre' es obligatorio
        response = self.client.post(self.url_listado_clientes, data_invalida, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_administrador_puede_actualizar_cliente(self):
        """Un administrador puede modificar los campos de un cliente mediante PUT (200 OK)"""
        self.autenticar_cliente(self.usuario_admin)
        data_actualizada = {
            "nombre": "Insumos Tecnológicos Modificado S.A.",
            "telefono": "3584000000"
        }
        response = self.client.put(self.url_detalle_cliente, data_actualizada, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validamos que se haya impactado el cambio real en la Base de Datos
        self.cliente_api.refresh_from_db()
        self.assertEqual(self.cliente_api.nombre, "Insumos Tecnológicos Modificado S.A.")

    def test_administrador_puede_eliminar_cliente(self):
        """Un administrador puede dar de baja un cliente mediante DELETE (204 No Content)"""
        self.autenticar_cliente(self.usuario_admin)
        response = self.client.delete(self.url_detalle_cliente)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cliente.objects.filter(pk=self.cliente_api.pk).exists())

    def test_cliente_no_encontrado_devuelve_404(self):
        """Cualquier consulta o acción sobre un ID de cliente inexistente debe retornar 404 Not Found"""
        self.autenticar_cliente(self.usuario_admin)
        url_inexistente = '/api/v3/clientes/99999/'
        response = self.client.get(url_inexistente)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)