from rest_framework import serializers
from .models import Cliente, Cotizacion, CotizacionItem, Factura, Producto


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        # Campos explícitos para evitar sobreexposición y permitir control de read_only
        fields = (
            "id",
            "nombre",
            "email",
            "telefono",
            "direccion",
            "localidad",
            "activo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = (
            "id",
            "nombre",
            "descripcion",
            "tipo",
            "precio_unitario",
            "stock",
            "proveedor",
            "activo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CotizacionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotizacionItem
        fields = (
            "id",
            "cotizacion",
            "producto",
            "cantidad",
            "precio_unitario",
            "subtotal",
        )
        read_only_fields = ("id", "subtotal")


class CotizacionSerializer(serializers.ModelSerializer):
    items = CotizacionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cotizacion
        fields = (
            "id",
            "numero",
            "cliente",
            "tipo_documento",
            "fecha",
            "observaciones",
            "descuento_porcentaje",
            "subtotal_bruto",
            "monto_descuento",
            "total",
            "usuario",
            "estado",
            "email_enviado",
            "created_at",
            "updated_at",
            "items",
        )
        read_only_fields = ("id", "subtotal_bruto", "monto_descuento", "total", "created_at", "updated_at")


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = (
            "id",
            "cliente",
            "tipo",
            "punto_venta",
            "numero",
            "fecha",
            "neto",
            "total",
            "cae",
            "cae_vencimiento",
            "estado",
            "creada",
            "usuario",
        )
        read_only_fields = ("id", "creada")
