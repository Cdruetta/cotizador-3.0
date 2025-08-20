from django.contrib import admin
from ..models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'localidad', 'email', 'created_at']
    list_filter = ['localidad', 'created_at']
    search_fields = ['nombre', 'telefono', 'email']
    ordering = ['nombre']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['nombre', 'contacto', 'email']
    ordering = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'proveedor', 'precio_unitario', 'activo', 'created_at']
    list_filter = ['proveedor', 'activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

class CotizacionItemInline(admin.TabularInline):
    model = CotizacionItem
    extra = 1

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'tipo_documento', 'fecha', 'total', 'usuario']
    list_filter = ['tipo_documento', 'fecha', 'usuario']
    search_fields = ['numero', 'cliente__nombre']
    ordering = ['-fecha', '-numero']
    inlines = [CotizacionItemInline]
