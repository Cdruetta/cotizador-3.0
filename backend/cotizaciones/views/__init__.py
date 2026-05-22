"""
Paquete de vistas.

Re-exporta símbolos para mantener compatibilidad con imports existentes:
`from cotizaciones import views` y `from cotizaciones.views import X`.
"""

from .dashboard import dashboard, reportes  # noqa: F401
from .auth import register  # noqa: F401
from .users import UserListView, UserCreateView  # noqa: F401
from .clientes import (  # noqa: F401
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    ClienteDetailView,
)
from .proveedores import (  # noqa: F401
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
    ProveedorDetailView,
)
from .productos import (  # noqa: F401
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    ProductoDetailView,
)
from .cotizaciones import (  # noqa: F401
    CotizacionListView,
    CotizacionCreateView,
    CotizacionUpdateView,
    CotizacionDeleteView,
    CotizacionDetailView,
    cambiar_estado_cotizacion,
    agregar_item_cotizacion,
    eliminar_item_cotizacion,
    generar_pdf,
    enviar_cotizacion_email,
)
from .api import get_producto_precio  # noqa: F401
from .config import configuracion  # noqa: F401

# ==============================================================================
# 🔌 RE-EXPORTACIÓN DE LA NUEVA API REST (Punto 4: CRUD, Roles y Filtros)
# ==============================================================================
from .api import (  # noqa: F401
    ClienteViewSet,
    ProductoViewSet,
    CotizacionViewSet,
    CotizacionItemViewSet,  # <-- Nombre real corregido
    FacturaViewSet,
)