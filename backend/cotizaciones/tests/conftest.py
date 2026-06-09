from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from model_bakery import baker

from ..models import Cliente, Proveedor, Producto, Categoria, Marca


@pytest.fixture
def usuario_comun(db):
    return User.objects.create_user(
        username="empleado", password="pass1234", email="emp@test.com"
    )


@pytest.fixture
def usuario_admin(db):
    return User.objects.create_user(
        username="admin",
        password="admin1234",
        email="admin@test.com",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def cliente(db):
    return Cliente.objects.create(
        nombre="Cliente SA",
        email="cli@test.com",
        telefono="3584112233",
        direccion="Calle Falsa 123",
        localidad="Rio Cuarto",
    )


@pytest.fixture
def proveedor(db):
    return Proveedor.objects.create(
        nombre="Proveedor SA",
        email="prov@test.com",
        telefono="3584112244",
    )


@pytest.fixture
def producto(db, proveedor):
    return Producto.objects.create(
        nombre="Producto Test",
        descripcion="Descripción del producto",
        precio_unitario=Decimal("100.00"),
        proveedor=proveedor,
        stock=50,
        tipo="producto",
    )


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="Categoria Test")


@pytest.fixture
def marca(db):
    return Marca.objects.create(nombre="Marca Test")


@pytest.fixture
def cotizacion_data(cliente, usuario_admin):
    """Datos mínimos para crear una cotización via API"""
    return {
        "numero": "COT-TEST-001",
        "cliente": cliente.pk,
        "tipo_documento": "presupuesto",
        "usuario": usuario_admin.pk,
    }


@pytest.fixture
def producto_data(proveedor):
    """Datos mínimos para crear un producto via API"""
    return {
        "nombre": "Nuevo Producto",
        "precio_unitario": "500.00",
        "proveedor": proveedor.pk,
        "tipo": "producto",
    }
