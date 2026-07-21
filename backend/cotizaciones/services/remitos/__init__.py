from ...models import Remito


def remito_queryset_filtrado(request):
    qs = Remito.objects.select_related("cliente", "usuario")
    estado = request.GET.get("estado")
    if estado:
        qs = qs.filter(estado=estado)
    busqueda = request.GET.get("q", "").strip()
    if busqueda:
        qs = qs.filter(numero__icontains=busqueda) | qs.filter(cliente__nombre__icontains=busqueda)
    return qs
