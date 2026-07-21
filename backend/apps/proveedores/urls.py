from django.urls import path
from apps.proveedores import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('crear/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('<int:pk>/', views.ProveedorDetailView.as_view(), name='proveedor_detail'),
    path('<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('<int:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),
]