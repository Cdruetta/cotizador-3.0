from django.urls import path
from apps.compras import views

app_name = 'compras'

urlpatterns = [
    path('', views.CompraListView.as_view(), name='compra_list'),
    path('crear/', views.CompraCreateView.as_view(), name='compra_create'),
    path('<int:pk>/', views.CompraDetailView.as_view(), name='compra_detail'),
    path('<int:pk>/editar/', views.CompraUpdateView.as_view(), name='compra_update'),
    path('<int:pk>/eliminar/', views.CompraDeleteView.as_view(), name='compra_delete'),
    path('<int:compra_id>/agregar-item/', views.agregar_item_compra, name='compra_add_item'),
    path('items/<int:item_id>/eliminar/', views.eliminar_item_compra, name='compra_delete_item'),
]