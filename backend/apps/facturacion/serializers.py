from rest_framework import serializers
from .models import Factura


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
