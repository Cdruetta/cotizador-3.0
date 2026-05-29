from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin

from ..models.compras import Compra, CompraItem
from ..forms.compras import CompraForm, CompraItemForm


class CompraListView(LoginRequiredMixin, ListView):
    model = Compra
    template_name = "cotizaciones/compra/list.html"
    context_object_name = "compras"
    paginate_by = 10

    def get_queryset(self):
        qs = Compra.objects.select_related("proveedor", "usuario")
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            qs = qs.filter(numero__icontains=busqueda) | qs.filter(proveedor__nombre__icontains=busqueda)
        estado = self.request.GET.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["compras"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        ctx["total_compras"] = Compra.objects.count()
        ctx["compras_pendientes"] = Compra.objects.filter(estado="pendiente").count()
        ctx["filtro_estado"] = self.request.GET.get("estado", "")
        return ctx


class CompraCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Compra
    form_class = CompraForm
    template_name = "cotizaciones/compra/form.html"
    success_message = "Compra creada correctamente."

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("compra_detail", kwargs={"pk": self.object.pk})


class CompraUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = "cotizaciones/compra/form.html"
    success_message = "Compra actualizada correctamente."

    def get_success_url(self):
        return reverse_lazy("compra_detail", kwargs={"pk": self.object.pk})


class CompraDeleteView(LoginRequiredMixin, DeleteView):
    model = Compra
    success_url = reverse_lazy("compra_list")
    success_message = "Compra eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class CompraDetailView(LoginRequiredMixin, DetailView):
    model = Compra
    template_name = "cotizaciones/compra/detail.html"
    context_object_name = "compra"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = self.object.items.select_related("producto")
        ctx["item_form"] = CompraItemForm()
        return ctx


@login_required
def agregar_item_compra(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    if request.method == "POST":
        form = CompraItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.compra = compra
            item.save()
            compra.actualizar_totales()
            messages.success(request, "Producto agregado.")
    return redirect("compra_detail", pk=compra_id)


@login_required
def eliminar_item_compra(request, item_id):
    item = get_object_or_404(CompraItem, id=item_id)
    compra_id = item.compra.id
    item.delete()
    item.compra.actualizar_totales()
    messages.success(request, "Producto eliminado.")
    return redirect("compra_detail", pk=compra_id)
