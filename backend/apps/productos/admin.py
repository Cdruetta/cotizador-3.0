from django.contrib import admin
from .models import Producto, Proveedor, Categoria, Marca, ListaPrecio, ListaPrecioItem


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "proveedor", "precio_unitario", "activo", "created_at"]
    list_filter = ["proveedor", "activo", "created_at"]
    search_fields = ["nombre", "descripcion"]
    ordering = ["nombre"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "created_at"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    ordering = ["nombre"]


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "created_at"]
    list_filter = ["activo"]
    search_fields = ["nombre"]
    ordering = ["nombre"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["nombre", "email", "telefono", "contacto"]
    search_fields = ["nombre", "email", "contacto"]
    ordering = ["nombre"]


@admin.register(ListaPrecio)
class ListaPrecioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "porcentaje", "por_defecto", "activo", "created_at"]
    list_filter = ["activo", "por_defecto"]
    search_fields = ["nombre"]


@admin.register(ListaPrecioItem)
class ListaPrecioItemAdmin(admin.ModelAdmin):
    list_display = ["lista", "categoria", "servicio", "precio", "orden"]
    list_filter = ["lista"]
    search_fields = ["categoria", "servicio"]
