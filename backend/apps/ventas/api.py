from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Cotizacion, CotizacionItem
from .serializers import CotizacionSerializer, CotizacionItemSerializer
from apps.core.api import EsAdministradorOReadOnly


class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["estado", "tipo_documento"]
    search_fields = ["numero", "observaciones", "cliente__nombre"]
    ordering_fields = ["fecha", "total", "id"]
    ordering = ["-fecha"]


class CotizacionItemViewSet(viewsets.ModelViewSet):
    queryset = CotizacionItem.objects.all()
    serializer_class = CotizacionItemSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["cotizacion", "producto"]


@login_required
def pending_cotizaciones_count(request):
    count = Cotizacion.objects.filter(estado="borrador").count()
    return JsonResponse({"count": count})


@login_required
def pending_cotizaciones_list(request):
    cotizaciones = Cotizacion.objects.filter(estado="borrador").order_by("-fecha")
    data = []
    for cot in cotizaciones:
        data.append(
            {
                "id": cot.id,
                "numero": cot.numero,
                "cliente": cot.cliente.nombre,
                "fecha": cot.fecha.strftime("%Y-%m-%d") if cot.fecha else None,
                "total": str(cot.total),
                "url": reverse("cotizacion_detail", kwargs={"pk": cot.pk}),
            }
        )
    return JsonResponse({"cotizaciones": data})
