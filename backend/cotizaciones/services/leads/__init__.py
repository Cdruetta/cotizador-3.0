from ...models.leads import Lead


def lead_queryset_filtrado(request):
    qs = Lead.objects.all()
    estado = request.GET.get("estado")
    if estado:
        qs = qs.filter(estado=estado)
    fuente = request.GET.get("fuente")
    if fuente:
        qs = qs.filter(fuente=fuente)
    busqueda = request.GET.get("q", "").strip()
    if busqueda:
        qs = qs.filter(nombre__icontains=busqueda)
    return qs
