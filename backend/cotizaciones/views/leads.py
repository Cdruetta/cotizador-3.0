from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from ..forms.leads import LeadForm
from ..models import Lead
from ..services.leads import lead_queryset_filtrado


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = "cotizaciones/lead/list.html"
    context_object_name = "leads"
    paginate_by = 10

    def get_queryset(self):
        return lead_queryset_filtrado(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_leads"] = Lead.objects.count()
        ctx["leads_nuevos"] = Lead.objects.filter(estado="nuevo").count()
        ctx["filtro_estado"] = self.request.GET.get("estado", "")
        ctx["filtro_fuente"] = self.request.GET.get("fuente", "")
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["leads"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "cotizaciones/lead/form.html"
    success_url = reverse_lazy("lead_list")

    def form_valid(self, form):
        form.instance.asignado_a = self.request.user
        return super().form_valid(form)


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "cotizaciones/lead/form.html"
    success_url = reverse_lazy("lead_list")


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    success_url = reverse_lazy("lead_list")
