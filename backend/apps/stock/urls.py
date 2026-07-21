from django.urls import path
from apps.stock import views

app_name = 'stock'

urlpatterns = [
    path('', views.StockListView.as_view(), name='stock_list'),
    path('exportar/excel/', views.exportar_stock_excel, name='stock_exportar_excel'),
    path('exportar/pdf/', views.exportar_stock_pdf, name='stock_exportar_pdf'),
    path('importar/', views.importar_stock_excel, name='stock_importar_excel'),
    path('movimientos/', views.MovimientoStockListView.as_view(), name='movimiento_stock_list'),
    path('movimientos/crear/', views.MovimientoStockCreateView.as_view(), name='movimiento_stock_create'),
]