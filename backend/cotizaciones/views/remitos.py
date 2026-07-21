from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ..forms.remitos import RemitoForm
from ..models import Remito
from ..services.remitos import remito_queryset_filtrado


class RemitoListView(LoginRequiredMixin, ListView):
    model = Remito
    template_name = "cotizaciones/remito/list.html"
    context_object_name = "remitos"
    paginate_by = 10

    def get_queryset(self):
        return remito_queryset_filtrado(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_remitos"] = Remito.objects.count()
        ctx["remitos_pendientes"] = Remito.objects.filter(estado="pendiente").count()
        ctx["filtro_estado"] = self.request.GET.get("estado", "")
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["remitos"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class RemitoCreateView(LoginRequiredMixin, CreateView):
    model = Remito
    form_class = RemitoForm
    template_name = "cotizaciones/remito/form.html"
    success_url = reverse_lazy("remito_list")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class RemitoUpdateView(LoginRequiredMixin, UpdateView):
    model = Remito
    form_class = RemitoForm
    template_name = "cotizaciones/remito/form.html"
    success_url = reverse_lazy("remito_list")


class RemitoDeleteView(LoginRequiredMixin, DeleteView):
    model = Remito
    success_url = reverse_lazy("remito_list")
