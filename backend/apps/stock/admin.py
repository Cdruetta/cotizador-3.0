from django.contrib import admin
from .models import MovimientoStock


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ["producto", "tipo", "cantidad", "stock_resultante", "usuario", "created_at"]
    list_filter = ["tipo", "created_at"]
    search_fields = ["producto__nombre", "motivo"]
