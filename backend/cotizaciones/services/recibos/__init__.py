from ...models.recibos import Recibo


def recibo_queryset_filtrado(usuario=None):
    qs = Recibo.objects.select_related("cliente", "usuario")
    if usuario and not usuario.is_superuser:
        qs = qs.filter(usuario=usuario)
    return qs
