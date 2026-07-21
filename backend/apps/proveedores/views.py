from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.productos.forms import ProveedorForm
from apps.productos.models import Proveedor


class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = "cotizaciones/proveedor/list.html"
    context_object_name = "proveedores"
    paginate_by = 10

    def get_queryset(self):
        qs = Proveedor.objects.all()
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(contacto__icontains=search))
        return qs


class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "cotizaciones/proveedor/form.html"
    success_url = reverse_lazy("proveedor_list")

    def form_valid(self, form):
        messages.success(self.request, "Proveedor creado exitosamente.")
        return super().form_valid(form)


class ProveedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "cotizaciones/proveedor/form.html"
    success_url = reverse_lazy("proveedor_list")

    def form_valid(self, form):
        messages.success(self.request, "Proveedor actualizado exitosamente.")
        return super().form_valid(form)


class ProveedorDeleteView(LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = "cotizaciones/proveedor/confirm_delete.html"
    success_url = reverse_lazy("proveedor_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Proveedor eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class ProveedorDetailView(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = "cotizaciones/proveedor/detail.html"
    context_object_name = "proveedor"
