from .clientes import ClienteForm  # noqa: F401
from .proveedores import ProveedorForm  # noqa: F401
from .productos import ProductoForm, ProductoFilterForm  # noqa: F401
from .cotizaciones import (  # noqa: F401
    CotizacionForm,
    CotizacionItemForm,
    CotizacionFilterForm,
    EnviarEmailForm,
)
from .usuarios import CustomUserCreationForm  # noqa: F401
from .config import ConfiguracionForm  # noqa: F401
from .leads import LeadForm  # noqa: F401
from .remitos import RemitoForm  # noqa: F401
from .recibos import ReciboForm  # noqa: F401
from .categorias import CategoriaForm  # noqa: F401
from .marcas import MarcaForm  # noqa: F401
from .compras import CompraForm, CompraItemForm  # noqa: F401
from .movimientos_stock import MovimientoStockForm  # noqa: F401
from .listas_precio import ListaPrecioForm  # noqa: F401
from .roles import GroupForm  # noqa: F401
from .tienda_web import TiendaWebConfigForm  # noqa: F401

