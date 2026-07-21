from django.urls import path
from apps.clientes import views

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='cliente_list'),
    path('crear/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    path('<int:pk>/toggle-activo/', views.toggle_cliente_activo, name='toggle_cliente_activo'),
    path('importar-excel/', views.importar_clientes_excel, name='importar_clientes_excel'),
    path('exportar-excel/', views.exportar_clientes_excel, name='exportar_clientes_excel'),
    path('exportar-pdf/', views.exportar_clientes_pdf, name='exportar_clientes_pdf'),
    # Leads
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/crear/', views.LeadCreateView.as_view(), name='lead_create'),
    path('leads/<int:pk>/', views.LeadUpdateView.as_view(), name='lead_update'),
    path('leads/<int:pk>/eliminar/', views.LeadDeleteView.as_view(), name='lead_delete'),
]