from django.urls import path
from apps.ventas import views

app_name = 'ventas'

urlpatterns = [
    # Cotizaciones
    path('cotizaciones/', views.CotizacionListView.as_view(), name='cotizacion_list'),
    path('cotizaciones/crear/', views.CotizacionCreateView.as_view(), name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', views.CotizacionDetailView.as_view(), name='cotizacion_detail'),
    path('cotizaciones/<int:pk>/editar/', views.CotizacionUpdateView.as_view(), name='cotizacion_update'),
    path('cotizaciones/<int:pk>/eliminar/', views.CotizacionDeleteView.as_view(), name='cotizacion_delete'),
    path('cotizaciones/<int:cotizacion_id>/descuento/', views.actualizar_descuento_cotizacion, name='actualizar_descuento_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/pdf/', views.generar_pdf, name='generar_pdf'),
    path('cotizaciones/<int:cotizacion_id>/estado/<str:estado>/', views.cambiar_estado_cotizacion, name='cambiar_estado_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/crear-factura/', views.crear_factura_desde_cotizacion, name='crear_factura_desde_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/agregar-item/', views.agregar_item_cotizacion, name='agregar_item_cotizacion'),
    path('items/<int:item_id>/eliminar/', views.eliminar_item_cotizacion, name='eliminar_item_cotizacion'),
    path('cotizaciones/<int:cotizacion_id>/enviar-email/', views.enviar_cotizacion_email, name='enviar_cotizacion_email'),
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
    # Remitos
    path('remitos/', views.RemitoListView.as_view(), name='remito_list'),
    path('remitos/crear/', views.RemitoCreateView.as_view(), name='remito_create'),
    path('remitos/<int:pk>/editar/', views.RemitoUpdateView.as_view(), name='remito_update'),
    path('remitos/<int:pk>/eliminar/', views.RemitoDeleteView.as_view(), name='remito_delete'),
]