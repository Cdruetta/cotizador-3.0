from io import BytesIO, StringIO
import csv

import pytest
from django.db import transaction

from ..models import Cliente, Producto, Proveedor
from ..services.clientes.import_excel import importar_clientes_desde_archivo
from ..services.productos.import_excel import importar_productos_desde_archivo


def _make_csv(headers: list[str], rows: list[list[str]]) -> BytesIO:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    buffer.seek(0)
    bio = BytesIO(buffer.getvalue().encode("utf-8-sig"))
    bio.name = "test.csv"
    return bio


def _make_xlsx(headers: list[str], rows: list[list]) -> BytesIO:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    bio.name = "test.xlsx"
    return bio


@pytest.mark.django_db
class TestImportarClientes:
    """Tests para importar_clientes_desde_archivo"""

    def test_csv_crea_varios_clientes(self):
        archivo = _make_csv(
            ["nombre", "email", "telefono"],
            [["Cliente A", "a@a.com", "111"], ["Cliente B", "b@b.com", "222"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 2
        assert resultado["errores"] == []
        assert Cliente.objects.count() == 2

    def test_xlsx_crea_clientes(self):
        archivo = _make_xlsx(
            ["nombre", "email"],
            [["Test XLSX", "xlsx@test.com"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert Cliente.objects.filter(nombre="Test XLSX").exists()

    def test_faltante_nombre_falla(self):
        archivo = _make_csv(["email"], [["a@a.com"]])
        with pytest.raises(ValueError, match="No se encontró la columna"):
            importar_clientes_desde_archivo(archivo)

    def test_fila_con_nombre_vacio_se_salta(self):
        archivo = _make_csv(
            ["nombre", "email"],
            [["", "a@a.com"], ["Valido", "b@b.com"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert resultado["errores"] == []

    def test_columna_email_invalido_se_reporta_error(self):
        archivo = _make_csv(
            ["nombre", "email"],
            [["Test", "email-invalido"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert len(resultado["errores"]) >= 0

    def test_activo_false_se_interpreta(self):
        archivo = _make_csv(
            ["nombre", "activo"],
            [["Inactivo", "no"], ["Activo", "si"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 2
        assert not Cliente.objects.get(nombre="Inactivo").activo
        assert Cliente.objects.get(nombre="Activo").activo

    def test_upsert_por_email_actualiza(self):
        Cliente.objects.create(nombre="Original", email="x@x.com", telefono="000")
        archivo = _make_csv(
            ["nombre", "email", "telefono"],
            [["Actualizado", "x@x.com", "999"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["actualizados"] == 1
        c = Cliente.objects.get(email="x@x.com")
        assert c.nombre == "Actualizado"
        assert c.telefono == "999"

    def test_alias_de_columnas(self):
        archivo = _make_csv(
            ["Razón Social", "Teléfono"],
            [["Cliente Alias", "123"]],
        )
        resultado = importar_clientes_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert Cliente.objects.filter(nombre="Cliente Alias").exists()


@pytest.mark.django_db
class TestImportarProductos:
    """Tests para importar_productos_desde_archivo"""

    def test_csv_crea_productos(self):
        Proveedor.objects.create(nombre="Prov Test")
        archivo = _make_csv(
            ["nombre", "proveedor", "precio", "stock"],
            [["Prod A", "Prov Test", "100.50", "10"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert Producto.objects.filter(nombre="Prod A").exists()

    def test_xlsx_crea_productos(self):
        Proveedor.objects.create(nombre="Prov XLSX")
        archivo = _make_xlsx(
            ["nombre", "proveedor", "precio_unitario"],
            [["Prod XLSX", "Prov XLSX", "200"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        p = Producto.objects.get(nombre="Prod XLSX")
        assert p.precio_unitario == 200

    def test_faltante_nombre_falla(self):
        archivo = _make_csv(["stock"], [["10"]])
        with pytest.raises(ValueError, match="No se encontró la columna"):
            importar_productos_desde_archivo(archivo)

    def test_fila_sin_nombre_se_salta(self):
        Proveedor.objects.create(nombre="Prov")
        archivo = _make_csv(
            ["nombre", "proveedor"],
            [["", "Prov"], ["Real", "Prov"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1

    def test_precio_con_signo_peso(self):
        Proveedor.objects.create(nombre="Prov")
        archivo = _make_csv(
            ["nombre", "proveedor", "precio"],
            [["Prod $", "Prov", "$ 1500.50"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        p = Producto.objects.get(nombre="Prod $")
        assert p.precio_unitario == 1500.50

    def test_proveedor_no_existe_se_crea_automaticamente(self):
        archivo = _make_csv(
            ["nombre", "proveedor"],
            [["Prod Sin Prov", "Nuevo Proveedor"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert Proveedor.objects.filter(nombre="Nuevo Proveedor").exists()

    def test_upsert_por_nombre_actualiza(self):
        prov = Proveedor.objects.create(nombre="Prov")
        Producto.objects.create(nombre="Existente", proveedor=prov, stock=0)
        archivo = _make_csv(
            ["nombre", "stock", "proveedor"],
            [["Existente", "99", "Prov"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["actualizados"] == 1
        p = Producto.objects.get(nombre="Existente")
        assert p.stock == 99

    def test_tipo_servicio_software(self):
        Proveedor.objects.create(nombre="Prov")
        archivo = _make_csv(
            ["nombre", "tipo", "proveedor"],
            [["Serv Soft", "servicio_soft", "Prov"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        p = Producto.objects.get(nombre="Serv Soft")
        assert p.tipo == "servicio_soft"

    def test_alias_de_columnas(self):
        Proveedor.objects.create(nombre="Prov")
        archivo = _make_csv(
            ["Producto", "Provider", "Price"],
            [["Alias Prod", "Prov", "75"]],
        )
        resultado = importar_productos_desde_archivo(archivo)
        assert resultado["creados"] == 1
        assert Producto.objects.filter(nombre="Alias Prod").exists()
