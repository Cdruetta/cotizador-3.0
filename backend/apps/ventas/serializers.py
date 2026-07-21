from rest_framework import serializers
from .models import Cotizacion, CotizacionItem


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
