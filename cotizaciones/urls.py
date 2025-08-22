from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Usuarios (si los tienes, si no, puedes omitir estas líneas o crearlas)
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
    path('productos/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    
    # Cotizaciones
    path('cotizaciones/', views.CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/crear/', views.CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', views.CotizacionDetailView.as_view(), name='cotizacion_detail'),
    path('cotizaciones/<int:pk>/editar/', views.CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/<int:pk>/eliminar/', views.CotizacionDeleteView.as_view(), name='cotizacion_delete'),
    path('cotizaciones/<int:cotizacion_id>/pdf/', views.generar_pdf, name='generar_pdf'),
    
    # API
    path('api/producto/<int:producto_id>/precio/', views.get_producto_precio, name='get_producto_precio'),
    path('cotizaciones/<int:cotizacion_id>/agregar-item/', views.agregar_item_cotizacion, name='agregar_item_cotizacion'),
    path('items/<int:item_id>/eliminar/', views.eliminar_item_cotizacion, name='eliminar_item_cotizacion'),
]
