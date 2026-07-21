from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Factura
from .serializers import FacturaSerializer
from apps.core.api import EsAdministradorOReadOnly


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "punto_venta"]
    search_fields = ["numero", "cae", "cliente__nombre"]
    ordering_fields = ["fecha", "id"]
