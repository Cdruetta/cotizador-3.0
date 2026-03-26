from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Cliente


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

