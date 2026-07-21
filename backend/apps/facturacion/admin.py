from django.contrib import admin
from .models import ConfiguracionAFIP, Factura, ItemFactura


@admin.register(ConfiguracionAFIP)
class ConfiguracionAFIPAdmin(admin.ModelAdmin):
    list_display = ["cuit", "razon_social", "punto_venta", "ambiente", "actualizado"]


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ["cliente", "tipo", "numero", "fecha", "total", "cae", "estado", "creada"]
    list_filter = ["tipo", "estado", "fecha"]
    search_fields = ["cliente__nombre"]
    ordering = ["-creada"]


@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ["factura", "descripcion", "cantidad", "precio_unit", "subtotal"]
