from django.urls import path
from apps.comprobantes import views

app_name = 'comprobantes'

urlpatterns = [
    path('', views.ComprobanteListView.as_view(), name='comprobante_list'),
]