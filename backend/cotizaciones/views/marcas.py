from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin

from ..models.marcas import Marca
from ..forms.marcas import MarcaForm


class MarcaListView(LoginRequiredMixin, ListView):
    model = Marca
    template_name = "cotizaciones/marca/list.html"
    context_object_name = "marcas"
    paginate_by = 10

    def get_queryset(self):
        qs = Marca.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_marcas"] = Marca.objects.count()
        ctx["marcas_activas"] = Marca.objects.filter(activo=True).count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["marcas"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class MarcaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "cotizaciones/marca/form.html"
    success_url = reverse_lazy("marca_list")
    success_message = "Marca creada correctamente."


class MarcaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "cotizaciones/marca/form.html"
    success_url = reverse_lazy("marca_list")
    success_message = "Marca actualizada correctamente."


class MarcaDeleteView(LoginRequiredMixin, DeleteView):
    model = Marca
    success_url = reverse_lazy("marca_list")
    success_message = "Marca eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
