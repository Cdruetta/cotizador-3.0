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
    toggle_cliente_activo,
    importar_clientes_excel,
    exportar_clientes_excel,
    exportar_clientes_pdf,
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
    actualizar_descuento_cotizacion,
    buscar_productos_ajax,
)
from .api import get_producto_precio  # noqa: F401
from .config import configuracion  # noqa: F401
from .leads import LeadListView, LeadCreateView, LeadUpdateView, LeadDeleteView  # noqa: F401
from .remitos import RemitoListView, RemitoCreateView, RemitoUpdateView, RemitoDeleteView  # noqa: F401
from .comprobantes import ComprobanteListView  # noqa: F401
from .recibos import (  # noqa: F401
    ReciboListView, ReciboCreateView, ReciboUpdateView, ReciboDeleteView, ReciboDetailView,
    agregar_item_recibo, eliminar_item_recibo, generar_pdf_recibo, enviar_recibo_email,
)
from .categorias import CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView  # noqa: F401
from .marcas import MarcaListView, MarcaCreateView, MarcaUpdateView, MarcaDeleteView  # noqa: F401
from .movimientos_stock import MovimientoStockListView, MovimientoStockCreateView  # noqa: F401
from .stock import (StockListView, exportar_stock_excel, exportar_stock_pdf, importar_stock_excel)  # noqa: F401
from .compras import (  # noqa: F401
    CompraListView, CompraCreateView, CompraUpdateView, CompraDeleteView,
    CompraDetailView, agregar_item_compra, eliminar_item_compra,
)

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