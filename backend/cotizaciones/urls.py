from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    ProductoDetailView,
)

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

    # Autenticación
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),
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

    # Proveedores
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
    path('cotizaciones/', views.CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/crear/', views.CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', views.CotizacionDetailView.as_view(), name='cotizacion_detail'),
    path('cotizaciones/<int:pk>/editar/', views.CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/<int:pk>/eliminar/', views.CotizacionDeleteView.as_view(), name='cotizacion_delete'),

    path(
        'cotizaciones/<int:cotizacion_id>/pdf/',
        views.generar_pdf,
        name='generar_pdf'
    ),

    path(
        'cotizaciones/<int:cotizacion_id>/completar/',
        views.marcar_cotizacion_completada,
        name='marcar_cotizacion_completada'
    ),

    path(
        'cotizaciones/<int:cotizacion_id>/email/',
        views.enviar_cotizacion_email,
        name='enviar_cotizacion_email'
    ),

    path(
        'cotizaciones/<int:cotizacion_id>/crear-factura/',
        crear_factura_desde_cotizacion,
        name='crear_factura_desde_cotizacion'
    ),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),

    # Configuración
    path('configuracion/', views.configuracion, name='configuracion'),

    # API
    path(
        'api/producto/<int:producto_id>/precio/',
        views.get_producto_precio,
        name='get_producto_precio'
    ),

    path(
        'cotizaciones/<int:cotizacion_id>/agregar-item/',
        views.agregar_item_cotizacion,
        name='agregar_item_cotizacion'
    ),

    path(
        'items/<int:item_id>/eliminar/',
        views.eliminar_item_cotizacion,
        name='eliminar_item_cotizacion'
    ),

    # Facturación
    path('facturacion/', FacturaListView.as_view(), name='factura_list'),

    path(
        'facturacion/nueva/',
        FacturaCreateView.as_view(),
        name='factura_create'
    ),

    path(
        'facturacion/<int:pk>/',
        FacturaDetailView.as_view(),
        name='factura_detail'
    ),

    path(
        'facturacion/<int:factura_id>/items/',
        agregar_item_factura,
        name='factura_agregar_item'
    ),

    path(
        'facturacion/<int:factura_id>/autorizar/',
        autorizar_factura_view,
        name='factura_autorizar'
    ),

    path(
        'facturacion/<int:factura_id>/pdf/',
        generar_pdf_factura_view,
        name='generar_pdf_factura'
    ),

    # Configuración AFIP / ARCA
    path(
        'facturacion/configuracion/',
        configuracion_afip,
        name='facturacion_config'
    ),

    path(
        'facturacion/configuracion/csr/',
        generar_csr_view,
        name='facturacion_generar_csr'
    ),

    path(
        'facturacion/configuracion/test/',
        test_conexion_afip,
        name='facturacion_test'
    ),
]