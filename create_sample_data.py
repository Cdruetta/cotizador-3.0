# Script para crear datos de prueba
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')
django.setup()

from django.contrib.auth.models import User
from cotizaciones.models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem
from decimal import Decimal
from datetime import date

print("Creando datos de prueba...")

# Obtener o crear usuario admin
try:
    admin_user = User.objects.get(username='admin')
except User.DoesNotExist:
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema'
    )

# Crear clientes de ejemplo
clientes_data = [
    {
        'nombre': 'Juan Pérez',
        'direccion': 'Av. Libertador 1234',
        'telefono': '011-4567-8901',
        'localidad': 'Buenos Aires',
        'email': 'juan.perez@email.com'
    },
    {
        'nombre': 'María González',
        'direccion': 'San Martín 567',
        'telefono': '011-2345-6789',
        'localidad': 'Córdoba',
        'email': 'maria.gonzalez@email.com'
    },
    {
        'nombre': 'Carlos López',
        'direccion': 'Belgrano 890',
        'telefono': '011-3456-7890',
        'localidad': 'Rosario',
        'email': 'carlos.lopez@email.com'
    },
    {
        'nombre': 'Ana Martínez',
        'direccion': 'Mitre 345',
        'telefono': '011-4567-8901',
        'localidad': 'La Plata',
        'email': 'ana.martinez@email.com'
    },
    {
        'nombre': 'Roberto Silva',
        'direccion': 'Rivadavia 678',
        'telefono': '011-5678-9012',
        'localidad': 'Mendoza',
        'email': 'roberto.silva@email.com'
    }
]

for cliente_data in clientes_data:
    cliente, created = Cliente.objects.get_or_create(
        nombre=cliente_data['nombre'],
        defaults=cliente_data
    )
    if created:
        print(f"✅ Cliente creado: {cliente.nombre}")

# Crear proveedores de ejemplo
proveedores_data = [
    {
        'nombre': 'TechSupply SA',
        'contacto': 'Pedro Rodríguez',
        'direccion': 'Av. Corrientes 1500',
        'telefono': '011-6789-0123',
        'email': 'ventas@techsupply.com'
    },
    {
        'nombre': 'Informática Total',
        'contacto': 'Laura Fernández',
        'direccion': 'Florida 800',
        'telefono': '011-7890-1234',
        'email': 'info@informaticatotal.com'
    },
    {
        'nombre': 'Componentes PC',
        'contacto': 'Miguel Torres',
        'direccion': 'Lavalle 1200',
        'telefono': '011-8901-2345',
        'email': 'contacto@componentespc.com'
    }
]

for proveedor_data in proveedores_data:
    proveedor, created = Proveedor.objects.get_or_create(
        nombre=proveedor_data['nombre'],
        defaults=proveedor_data
    )
    if created:
        print(f"✅ Proveedor creado: {proveedor.nombre}")

# Crear productos de ejemplo
productos_data = [
    {'nombre': 'Procesador Intel Core i5', 'descripcion': 'Procesador Intel Core i5 12400F', 'precio': '45000.00', 'proveedor': 'TechSupply SA'},
    {'nombre': 'Memoria RAM 16GB', 'descripcion': 'Memoria DDR4 16GB 3200MHz', 'precio': '12000.00', 'proveedor': 'TechSupply SA'},
    {'nombre': 'Disco SSD 500GB', 'descripcion': 'Disco sólido SATA 500GB', 'precio': '8500.00', 'proveedor': 'Informática Total'},
    {'nombre': 'Placa de Video GTX 1660', 'descripcion': 'Tarjeta gráfica NVIDIA GTX 1660 Super', 'precio': '85000.00', 'proveedor': 'Componentes PC'},
    {'nombre': 'Mother ASUS B450', 'descripcion': 'Motherboard ASUS B450M-A', 'precio': '15000.00', 'proveedor': 'TechSupply SA'},
    {'nombre': 'Fuente 650W', 'descripcion': 'Fuente de poder 650W 80+ Bronze', 'precio': '12500.00', 'proveedor': 'Componentes PC'},
    {'nombre': 'Gabinete ATX', 'descripcion': 'Gabinete ATX con ventiladores', 'precio': '8000.00', 'proveedor': 'Informática Total'},
    {'nombre': 'Monitor 24"', 'descripcion': 'Monitor LED 24 pulgadas Full HD', 'precio': '35000.00', 'proveedor': 'Informática Total'},
    {'nombre': 'Teclado Mecánico', 'descripcion': 'Teclado mecánico RGB', 'precio': '15000.00', 'proveedor': 'Componentes PC'},
    {'nombre': 'Mouse Gaming', 'descripcion': 'Mouse óptico para gaming', 'precio': '5500.00', 'proveedor': 'Componentes PC'}
]

for producto_data in productos_data:
    proveedor = Proveedor.objects.get(nombre=producto_data['proveedor'])
    producto, created = Producto.objects.get_or_create(
        nombre=producto_data['nombre'],
        defaults={
            'descripcion': producto_data['descripcion'],
            'precio_unitario': Decimal(producto_data['precio']),
            'proveedor': proveedor,
            'activo': True
        }
    )
    if created:
        print(f"✅ Producto creado: {producto.nombre}")

# Crear cotizaciones de ejemplo
cotizaciones_data = [
    {
        'numero': 'COT-001',
        'cliente': 'Juan Pérez',
        'tipo_documento': 'presupuesto',
        'observaciones': 'Cotización para armado de PC gaming'
    },
    {
        'numero': 'REC-001',
        'cliente': 'María González',
        'tipo_documento': 'recibo',
        'observaciones': 'Recibo por servicios de mantenimiento'
    },
    {
        'numero': 'COT-002',
        'cliente': 'Carlos López',
        'tipo_documento': 'presupuesto',
        'observaciones': 'Presupuesto para upgrade de equipo'
    }
]

for cot_data in cotizaciones_data:
    cliente = Cliente.objects.get(nombre=cot_data['cliente'])
    cotizacion, created = Cotizacion.objects.get_or_create(
        numero=cot_data['numero'],
        defaults={
            'cliente': cliente,
            'tipo_documento': cot_data['tipo_documento'],
            'observaciones': cot_data['observaciones'],
            'usuario': admin_user
        }
    )
    if created:
        print(f"✅ Cotización creada: {cotizacion.numero}")

# Agregar items a las cotizaciones
items_data = [
    {'cotizacion': 'COT-001', 'producto': 'Procesador Intel Core i5', 'cantidad': '1', 'precio': '45000.00'},
    {'cotizacion': 'COT-001', 'producto': 'Memoria RAM 16GB', 'cantidad': '2', 'precio': '12000.00'},
    {'cotizacion': 'COT-001', 'producto': 'Placa de Video GTX 1660', 'cantidad': '1', 'precio': '85000.00'},
    {'cotizacion': 'REC-001', 'producto': 'Monitor 24"', 'cantidad': '1', 'precio': '35000.00'},
    {'cotizacion': 'COT-002', 'producto': 'Disco SSD 500GB', 'cantidad': '1', 'precio': '8500.00'},
    {'cotizacion': 'COT-002', 'producto': 'Fuente 650W', 'cantidad': '1', 'precio': '12500.00'},
]

for item_data in items_data:
    cotizacion = Cotizacion.objects.get(numero=item_data['cotizacion'])
    producto = Producto.objects.get(nombre=item_data['producto'])
    
    item, created = CotizacionItem.objects.get_or_create(
        cotizacion=cotizacion,
        producto=producto,
        defaults={
            'cantidad': Decimal(item_data['cantidad']),
            'precio_unitario': Decimal(item_data['precio'])
        }
    )
    if created:
        print(f"✅ Item agregado: {producto.nombre} a {cotizacion.numero}")

print("\n🎉 ¡Datos de prueba creados exitosamente!")
print("\nPuedes iniciar sesión con:")
print("Usuario: admin")
print("Contraseña: admin123")
