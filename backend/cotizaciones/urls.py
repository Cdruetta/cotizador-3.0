from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    ProductoDetailView,

    CotizacionListView,
    CotizacionCreateView,
    CotizacionUpdateView,
    CotizacionDeleteView,
    CotizacionDetailView,

    agregar_item_cotizacion,
    eliminar_item_cotizacion,
    generar_pdf,
    cambiar_estado_cotizacion,
    enviar_cotizacion_email,
    actualizar_descuento_cotizacion,
    buscar_productos_ajax,
    configuracion,
)

# 🚀 IMPORTACIÓN DE LA API: Traemos get_producto_precio desde donde quedó alojada
from .views.api import get_producto_precio, pending_cotizaciones_count, pending_cotizaciones_list

# Importamos la nueva vista de reportes desde su archivo específico
from .views.reportes import reportes_view

from .views.facturacion import (
    configuracion_afip,
    generar_csr_view,
    test_conexion_afip,
    FacturaListView,
    FacturaCreateView,
    FacturaDetailView,
    agregar_item_factura,
    autorizar_factura_view,
    generar_pdf_factura_view,
    crear_factura_desde_cotizacion,
)

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Usuarios
    path('usuarios/', views.UserListView.as_view(), name='user_list'),
    path('usuarios/crear/', views.UserCreateView.as_view(), name='user_create'),

    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    path('clientes/<int:pk>/toggle-activo/', views.toggle_cliente_activo, name='cliente_toggle_activo'),
    path('clientes/importar/', views.importar_clientes_excel, name='cliente_importar_excel'),
    path('clientes/exportar/excel/', views.exportar_clientes_excel, name='cliente_exportar_excel'),
    path('clientes/exportar/pdf/', views.exportar_clientes_pdf, name='cliente_exportar_pdf'),

    # Proveedores (✨ Esto es lo que revive tu Dashboard sin errores)
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/crear/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/', views.ProveedorDetailView.as_view(), name='proveedor_detail'),
    path('proveedores/<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),

    # Productos
    path('productos/', ProductoListView.as_view(), name='producto_list'),
    path('productos/crear/', ProductoCreateView.as_view(), name='producto_create'),
    path('productos/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='producto_delete'),

    # Cotizaciones
    path('cotizaciones/', CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/crear/', CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', CotizacionDetailView.as_view(), name='cotizacion_detail'),
    path('cotizaciones/<int:pk>/editar/', CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/<int:pk>/eliminar/', CotizacionDeleteView.as_view(), name='cotizacion_delete'),

    # Descuento
    path('cotizaciones/<int:cotizacion_id>/descuento/', actualizar_descuento_cotizacion, name='actualizar_descuento_cotizacion'),

    # PDF
    path('cotizaciones/<int:cotizacion_id>/pdf/', generar_pdf, name='generar_pdf'),

    # Estado
    path('cotizaciones/<int:cotizacion_id>/estado/<str:estado>/', cambiar_estado_cotizacion, name='cambiar_estado_cotizacion'),

    # Factura desde cotización
    path('cotizaciones/<int:cotizacion_id>/crear-factura/', crear_factura_desde_cotizacion, name='crear_factura_desde_cotizacion'),

    # Items cotización
    path('cotizaciones/<int:cotizacion_id>/agregar-item/', agregar_item_cotizacion, name='agregar_item_cotizacion'),
    path('items/<int:item_id>/eliminar/', eliminar_item_cotizacion, name='eliminar_item_cotizacion'),

    # Email
    path('cotizaciones/<int:cotizacion_id>/enviar-email/', enviar_cotizacion_email, name='enviar_cotizacion_email'),

    # Leads / CRM
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/crear/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<int:pk>/editar/', views.LeadUpdateView.as_view(), name='lead_update'),
    path('leads/<int:pk>/eliminar/', views.LeadDeleteView.as_view(), name='lead_delete'),

    # Remitos
    path('remitos/', views.RemitoListView.as_view(), name='remito_list'),
    path('remitos/crear/', views.RemitoCreateView.as_view(), name='remito_create'),
    path('remitos/<int:pk>/editar/', views.RemitoUpdateView.as_view(), name='remito_update'),
    path('remitos/<int:pk>/eliminar/', views.RemitoDeleteView.as_view(), name='remito_delete'),

    # Comprobantes
    path('comprobantes/', views.ComprobanteListView.as_view(), name='comprobante_list'),

    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),

    # Marcas
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/crear/', views.MarcaCreateView.as_view(), name='marca_create'),
    path('marcas/<int:pk>/editar/', views.MarcaUpdateView.as_view(), name='marca_update'),
    path('marcas/<int:pk>/eliminar/', views.MarcaDeleteView.as_view(), name='marca_delete'),

    # Compras
    path('compras/', views.CompraListView.as_view(), name='compra_list'),
    path('compras/crear/', views.CompraCreateView.as_view(), name='compra_create'),
    path('compras/<int:pk>/', views.CompraDetailView.as_view(), name='compra_detail'),
    path('compras/<int:pk>/editar/', views.CompraUpdateView.as_view(), name='compra_update'),
    path('compras/<int:pk>/eliminar/', views.CompraDeleteView.as_view(), name='compra_delete'),
    path('compras/<int:compra_id>/agregar-item/', views.agregar_item_compra, name='compra_add_item'),
    path('compra-items/<int:item_id>/eliminar/', views.eliminar_item_compra, name='compra_delete_item'),

    # Stock
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/exportar/excel/', views.exportar_stock_excel, name='stock_exportar_excel'),
    path('stock/exportar/pdf/', views.exportar_stock_pdf, name='stock_exportar_pdf'),
    path('stock/importar/', views.importar_stock_excel, name='stock_importar_excel'),

    # Movimientos de stock
    path('stock/movimientos/', views.MovimientoStockListView.as_view(), name='movimiento_stock_list'),
    path('stock/movimientos/crear/', views.MovimientoStockCreateView.as_view(), name='movimiento_stock_create'),

    # Recibos
    path('recibos/', views.ReciboListView.as_view(), name='recibo_list'),
    path('recibos/crear/', views.ReciboCreateView.as_view(), name='recibo_create'),
    path('recibos/<int:pk>/', views.ReciboDetailView.as_view(), name='recibo_detail'),
    path('recibos/<int:pk>/editar/', views.ReciboUpdateView.as_view(), name='recibo_update'),
    path('recibos/<int:pk>/eliminar/', views.ReciboDeleteView.as_view(), name='recibo_delete'),
    path('recibos/<int:recibo_id>/pdf/', views.generar_pdf_recibo, name='recibo_pdf'),
    path('recibos/<int:recibo_id>/agregar-item/', views.agregar_item_recibo, name='recibo_add_item'),
    path('recibos/<int:recibo_id>/enviar-email/', views.enviar_recibo_email, name='recibo_email'),
    path('recibo-items/<int:item_id>/eliminar/', views.eliminar_item_recibo, name='recibo_delete_item'),

    # Reportes
    path('reportes/', reportes_view, name='reportes'),

    # Configuración
    path('configuracion/', configuracion, name='configuracion'),

    # API Tradicional Interna (Mapeada a .views.api)
    path('api/producto/<int:producto_id>/precio/', get_producto_precio, name='get_producto_precio'),
    path('api/pending-cotizaciones-count/', pending_cotizaciones_count, name='pending_cotizaciones_count'),
    path('api/pending-cotizaciones/', pending_cotizaciones_list, name='pending_cotizaciones_list'),
    path('api/productos/buscar/', buscar_productos_ajax, name='buscar_productos_ajax'),

    # Facturación
    path('facturacion/', FacturaListView.as_view(), name='factura_list'),
    path('facturacion/nueva/', FacturaCreateView.as_view(), name='factura_create'),
    path('facturacion/<int:pk>/', FacturaDetailView.as_view(), name='factura_detail'),
    path('facturacion/<int:factura_id>/items/', agregar_item_factura, name='factura_agregar_item'),
    path('facturacion/<int:factura_id>/autorizar/', autorizar_factura_view, name='factura_autorizar'),
    path('facturacion/<int:factura_id>/pdf/', generar_pdf_factura_view, name='generar_pdf_factura'),

    # AFIP
    path('facturacion/configuracion/', configuracion_afip, name='facturacion_config'),
    path('facturacion/configuracion/csr/', generar_csr_view, name='facturacion_generar_csr'),
    path('facturacion/configuracion/test/', test_conexion_afip, name='facturacion_test'),
]