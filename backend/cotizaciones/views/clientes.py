from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from ..forms import ClienteForm
from ..models import Cliente


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "cotizaciones/cliente/list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        qs = Cliente.objects.all()
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search)
                | Q(telefono__icontains=search)
                | Q(localidad__icontains=search)
            )
        return qs


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "cotizaciones/cliente/form.html"
    success_url = reverse_lazy("cliente_list")

    def form_valid(self, form):
        messages.success(self.request, "Cliente creado exitosamente.")
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "cotizaciones/cliente/form.html"
    success_url = reverse_lazy("cliente_list")

    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado exitosamente.")
        return super().form_valid(form)


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = "cotizaciones/cliente/confirm_delete.html"
    success_url = reverse_lazy("cliente_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cliente eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "cotizaciones/cliente/detail.html"
    context_object_name = "cliente"

