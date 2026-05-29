from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from ..models.facturacion import Factura


class ComprobanteListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = "cotizaciones/comprobante/list.html"
    context_object_name = "comprobantes"
    paginate_by = 10

    def get_queryset(self):
        qs = Factura.objects.select_related("cliente", "usuario")
        estado = self.request.GET.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        tipo = self.request.GET.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            qs = qs.filter(numero__icontains=busqueda) | qs.filter(cliente__nombre__icontains=busqueda)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_comprobantes"] = Factura.objects.count()
        ctx["comprobantes_pendientes"] = Factura.objects.filter(estado="borrador").count()
        ctx["comprobantes_autorizados"] = Factura.objects.filter(estado="autorizada").count()
        ctx["filtro_estado"] = self.request.GET.get("estado", "")
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["comprobantes"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx
