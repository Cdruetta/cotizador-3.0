from rest_framework import serializers
from .models import Cliente, Cotizacion, CotizacionItem, Factura, Producto

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class CotizacionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CotizacionItem
        fields = '__all__'

class CotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotizacion
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'