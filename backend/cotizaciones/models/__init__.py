from apps.core.models import Configuracion  # noqa: F401
from apps.clientes.models import Cliente, Lead  # noqa: F401
from apps.productos.models import Producto, Proveedor, Categoria, Marca, ListaPrecio, ListaPrecioItem  # noqa: F401
from apps.ventas.models import Cotizacion, CotizacionItem, Recibo, ReciboItem, Remito, RemitoItem  # noqa: F401
from apps.facturacion.models import ConfiguracionAFIP, Factura, ItemFactura  # noqa: F401
from apps.compras.models import Compra, CompraItem  # noqa: F401
from apps.stock.models import MovimientoStock  # noqa: F401
