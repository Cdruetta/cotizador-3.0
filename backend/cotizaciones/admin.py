from django.contrib import admin
from .models import Cliente, MovimientoStock, Proveedor, Producto, Cotizacion, CotizacionItem, Lead, Remito, RemitoItem, Recibo, Categoria, Marca, Compra, CompraItem

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'localidad', 'email', 'created_at']
    list_filter = ['localidad', 'created_at']
    search_fields = ['nombre', 'telefono', 'email']
    ordering = ['nombre']

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['numero', 'proveedor', 'fecha', 'total', 'estado', 'usuario', 'created_at']
    list_filter = ['estado', 'fecha']
    search_fields = ['numero', 'proveedor__nombre']
    ordering = ['-fecha', '-numero']

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_resultante', 'usuario', 'created_at']
    list_filter = ['tipo', 'created_at']
    search_fields = ['producto__nombre', 'motivo']

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

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'created_at']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']



@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'empresa', 'estado', 'fuente', 'asignado_a', 'created_at']
    list_filter = ['estado', 'fuente', 'created_at']
    search_fields = ['nombre', 'email', 'empresa']
    ordering = ['-created_at']

@admin.register(Remito)
class RemitoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha', 'estado', 'usuario', 'created_at']
    list_filter = ['estado', 'fecha']
    search_fields = ['numero', 'cliente__nombre']
    ordering = ['-fecha', '-numero']
