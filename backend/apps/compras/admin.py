from django.contrib import admin
from .models import Compra, CompraItem


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ["numero", "proveedor", "fecha", "total", "estado", "usuario", "created_at"]
    list_filter = ["estado", "fecha"]
    search_fields = ["numero", "proveedor__nombre"]
    ordering = ["-fecha", "-numero"]


@admin.register(CompraItem)
class CompraItemAdmin(admin.ModelAdmin):
    list_display = ["compra", "producto", "descripcion", "cantidad", "precio_unitario", "subtotal"]
