from django.contrib import admin
from .models import Cliente, Lead


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "telefono", "localidad", "email", "created_at"]
    list_filter = ["localidad", "created_at"]
    search_fields = ["nombre", "telefono", "email"]
    ordering = ["nombre"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["nombre", "email", "empresa", "estado", "fuente", "asignado_a", "created_at"]
    list_filter = ["estado", "fuente", "created_at"]
    search_fields = ["nombre", "email", "empresa"]
    ordering = ["-created_at"]
