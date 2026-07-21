from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Cliente
from .serializers import ClienteSerializer
from apps.core.api import EsAdministradorOReadOnly


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo"]
    search_fields = ["nombre", "email", "telefono"]
    ordering_fields = ["nombre", "id"]
