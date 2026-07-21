from django.contrib import admin
from .models import Cotizacion, CotizacionItem, Recibo, ReciboItem, Remito, RemitoItem


class CotizacionItemInline(admin.TabularInline):
    model = CotizacionItem
    extra = 1


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    inlines = [CotizacionItemInline]
    list_display = ["numero", "cliente", "tipo_documento", "fecha", "total", "usuario"]
    list_filter = ["tipo_documento", "fecha", "usuario"]
    search_fields = ["numero", "cliente__nombre"]
    ordering = ["-fecha", "-numero"]


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ["numero", "cliente", "fecha", "total", "forma_pago", "usuario", "created_at"]
    list_filter = ["forma_pago", "fecha"]
    search_fields = ["numero", "cliente__nombre"]
    ordering = ["-fecha", "-numero"]


@admin.register(Remito)
class RemitoAdmin(admin.ModelAdmin):
    list_display = ["numero", "cliente", "fecha", "estado", "usuario", "created_at"]
    list_filter = ["estado", "fecha"]
    search_fields = ["numero", "cliente__nombre"]
    ordering = ["-fecha", "-numero"]
