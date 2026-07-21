from django.urls import path
from apps.productos import views

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='producto_list'),
    path('crear/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/crear/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    # Marcas
    path('marcas/', views.MarcaListView.as_view(), name='marca_list'),
    path('marcas/crear/', views.MarcaCreateView.as_view(), name='marca_create'),
    path('marcas/<int:pk>/', views.MarcaUpdateView.as_view(), name='marca_update'),
    path('marcas/<int:pk>/eliminar/', views.MarcaDeleteView.as_view(), name='marca_delete'),
    # Listas de precios
    path('listas/', views.ListaPrecioListView.as_view(), name='lista_precio_list'),
    path('listas/crear/', views.ListaPrecioCreateView.as_view(), name='lista_precio_create'),
    path('listas/<int:pk>/', views.ListaPrecioDetailView.as_view(), name='lista_precio_detail'),
    path('listas/<int:pk>/editar/', views.ListaPrecioUpdateView.as_view(), name='lista_precio_update'),
    path('listas/<int:pk>/eliminar/', views.ListaPrecioDeleteView.as_view(), name='lista_precio_delete'),
    path('listas/<int:pk>/importar/', views.importar_csv_lista_precio, name='importar_csv_lista_precio'),
    path('listas/<int:pk>/exportar-pdf/', views.exportar_lista_precio_pdf, name='exportar_lista_precio_pdf'),
    path('listas/<int:pk>/aplicar/', views.aplicar_precios_lista, name='aplicar_precios_lista'),
    path('listas/<int:pk>/item/editar/', views.editar_item_lista_precio, name='editar_item_lista_precio'),
    path('listas/<int:pk>/item/eliminar/', views.eliminar_item_lista_precio, name='eliminar_item_lista_precio'),
    path('listas/<int:pk>/item/agregar/', views.agregar_item_lista_precio, name='agregar_item_lista_precio'),
]