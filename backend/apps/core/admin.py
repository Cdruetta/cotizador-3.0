from django.contrib import admin
from .models import Configuracion


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ["empresa_nombre", "empresa_direccion", "empresa_telefono", "empresa_email", "updated_at"]
