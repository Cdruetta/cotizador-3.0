from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin

from ..models import Categoria
from ..forms.categorias import CategoriaForm


class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "cotizaciones/categoria/list.html"
    context_object_name = "categorias"
    paginate_by = 10

    def get_queryset(self):
        qs = Categoria.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_categorias"] = Categoria.objects.count()
        ctx["categorias_activas"] = Categoria.objects.filter(activo=True).count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["categorias"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class CategoriaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "cotizaciones/categoria/form.html"
    success_url = reverse_lazy("categoria_list")
    success_message = "CategorÃ­a creada correctamente."


class CategoriaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "cotizaciones/categoria/form.html"
    success_url = reverse_lazy("categoria_list")
    success_message = "CategorÃ­a actualizada correctamente."


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    success_url = reverse_lazy("categoria_list")
    success_message = "CategorÃ­a eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
