from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from ..forms import ProductoForm, ProductoFilterForm
from ..models import Producto


class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "cotizaciones/producto/list.html"
    context_object_name = "productos"
    paginate_by = 15

    def get_queryset(self):
        qs = Producto.objects.select_related("proveedor")
        form = ProductoFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get("search")
            proveedor = form.cleaned_data.get("proveedor")
            activo = form.cleaned_data.get("activo")
            precio_max = form.cleaned_data.get("precio_max")
            if search:
                qs = qs.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
            if proveedor:
                qs = qs.filter(proveedor=proveedor)
            if activo == "true":
                qs = qs.filter(activo=True)
            elif activo == "false":
                qs = qs.filter(activo=False)
            if precio_max:
                qs = qs.filter(precio_unitario__lte=precio_max)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = ProductoFilterForm(self.request.GET)
        return ctx


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "cotizaciones/producto/form.html"
    success_url = reverse_lazy("producto_list")

    def form_valid(self, form):
        messages.success(self.request, "Producto creado exitosamente.")
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "cotizaciones/producto/form.html"
    success_url = reverse_lazy("producto_list")

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado exitosamente.")
        return super().form_valid(form)


class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = "cotizaciones/producto/confirm_delete.html"
    success_url = reverse_lazy("producto_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Producto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = "cotizaciones/producto/detail.html"
    context_object_name = "producto"

