from django.urls import path
from apps.facturacion import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.FacturaListView.as_view(), name='factura_list'),
    path('nueva/', views.FacturaCreateView.as_view(), name='factura_create'),
    path('<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('<int:factura_id>/items/', views.agregar_item_factura, name='factura_agregar_item'),
    path('<int:factura_id>/autorizar/', views.autorizar_factura_view, name='factura_autorizar'),
    path('<int:factura_id>/pdf/', views.generar_pdf_factura_view, name='generar_pdf_factura'),
    # AFIP
    path('configuracion/', views.configuracion_afip, name='facturacion_config'),
    path('configuracion/csr/', views.generar_csr_view, name='facturacion_generar_csr'),
    path('configuracion/test/', views.test_conexion_afip, name='facturacion_test'),
]