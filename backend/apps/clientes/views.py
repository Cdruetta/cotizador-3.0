from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.clientes.forms import ClienteForm, ClienteImportForm, LeadForm
from apps.clientes.models import Cliente, Lead
from cotizaciones.services.clientes import (
    importar_clientes_desde_archivo,
    clientes_queryset_filtrado,
    exportar_clientes_excel_response,
    exportar_clientes_pdf_response,
)
from cotizaciones.services.leads import lead_queryset_filtrado


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "cotizaciones/cliente/list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        return clientes_queryset_filtrado(self.request)


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
    success_url = reverse_lazy("cliente_list")

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, "Cliente eliminado correctamente.")
            return super().delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                self.request,
                "No se puede eliminar el cliente porque tiene registros asociados.",
            )
            return redirect("cliente_list")


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "cotizaciones/cliente/detail.html"
    context_object_name = "cliente"


@login_required
@require_POST
def toggle_cliente_activo(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.activo = not cliente.activo
    cliente.save()
    messages.success(
        request,
        f"Cliente {'activado' if cliente.activo else 'desactivado'} correctamente.",
    )
    return redirect("cliente_list")


@login_required
def importar_clientes_excel(request):
    if request.method == "POST":
        form = ClienteImportForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES["archivo"]
            try:
                importar_clientes_desde_archivo(archivo)
                messages.success(request, "Clientes importados exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al importar clientes: {str(e)}")
            return redirect("cliente_list")
    else:
        form = ClienteImportForm()
    return render(request, "cotizaciones/cliente/import.html", {"form": form})


@login_required
def exportar_clientes_excel(request):
    return exportar_clientes_excel_response()


@login_required
def exportar_clientes_pdf(request):
    return exportar_clientes_pdf_response()


# ============================================
# LEADS VIEWS
# ============================================

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