"""
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
from .listas_precio import (  # noqa: F401
    ListaPrecioListView, ListaPrecioCreateView, ListaPrecioUpdateView,
    ListaPrecioDeleteView, ListaPrecioDetailView, importar_csv_lista_precio,
    exportar_lista_precio_pdf, aplicar_precios_lista,
    editar_item_lista_precio, eliminar_item_lista_precio, agregar_item_lista_precio,
)
from .tienda_web import tienda_web_config  # noqa: F401
from .roles import GroupListView, GroupCreateView, GroupUpdateView, GroupDeleteView  # noqa: F401
from .reportes import reportes_view  # noqa: F401
from .facturacion import (  # noqa: F401
    configuracion_afip, generar_csr_view, test_conexion_afip,
    FacturaListView, FacturaCreateView, FacturaDetailView,
    agregar_item_factura, autorizar_factura_view,
    generar_pdf_factura_view, crear_factura_desde_cotizacion,
)
from .api import (  # noqa: F401
    pending_cotizaciones_count, pending_cotizaciones_list,
    ClienteViewSet, ProductoViewSet, CotizacionViewSet,
    CotizacionItemViewSet, FacturaViewSet,
)