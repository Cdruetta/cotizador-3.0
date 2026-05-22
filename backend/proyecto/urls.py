from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# ==============================================================================
# 📚 CONFIGURACIÓN DE SWAGGER (DOCUMENTACIÓN INTERACTIVA)
# ==============================================================================
schema_view = get_schema_view(
   openapi.Info(
       title="API de Cotizaciones y Facturación",
       default_version='v3.0',
       description="Documentación interactiva de endpoints, filtros y autenticación JWT",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# ==============================================================================
# 🔌 ENRUTAMIENTO PRINCIPAL DEL BACKEND
# ==============================================================================
urlpatterns = [
    # 1. Panel de Administración tradicional de Django
    path('admin/', admin.site.urls),
    
    # 🚀 2. Endpoints de la API REST (CRUDs, Filtros y JWT)
    path('api/', include('proyecto.urls_api')),
    
    # 🏠 3. Tus vistas tradicionales actuales (Templates, formularios HTML y AFIP)
    path('', include('cotizaciones.urls')),
    
    # 📊 4. Swagger UI y ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Servir archivos multimedia (Media) y estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)