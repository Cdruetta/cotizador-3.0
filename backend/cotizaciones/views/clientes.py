from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from ..forms import ClienteForm
from ..forms.clientes import ClienteImportForm
from ..models import Cliente
from ..services.clientes import (
    importar_clientes_desde_archivo,
    clientes_queryset_filtrado,
    exportar_clientes_excel_response,
    exportar_clientes_pdf_response,
)


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "cotizaciones/cliente/list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        return clientes_queryset_filtrado(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_clientes"] = Cliente.objects.count()
        ctx["clientes_activos"] = Cliente.objects.filter(activo=True).count()
        ctx["clientes_con_saldo"] = 0
        ctx["deuda_total"] = 0
        ctx["filtro_estado"] = self.request.GET.get("estado", "activos")
        ctx["import_form"] = ClienteImportForm()
        page_obj = ctx.get("page_obj")
        if page_obj and page_obj.paginator.count:
            start = (page_obj.number - 1) * page_obj.paginator.per_page + 1
            end = start + len(ctx["clientes"]) - 1
            ctx["page_start"] = start
            ctx["page_end"] = end
            ctx["page_total"] = page_obj.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Cliente eliminado exitosamente.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.warning(
                request,
                "No se puede eliminar este cliente porque tiene facturas, cotizaciones, remitos o recibos asociados. "
                "Desactivá el cliente en su lugar."
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
    if request.POST.get("activo") in ("true", "1", "on"):
        cliente.activo = True
    elif request.POST.get("activo") in ("false", "0", "off"):
        cliente.activo = False
    else:
        cliente.activo = not cliente.activo
    cliente.save(update_fields=["activo"])
    return JsonResponse({"ok": True, "activo": cliente.activo})


@login_required
@require_POST
def importar_clientes_excel(request):
    form = ClienteImportForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Seleccioná un archivo válido (.xlsx o .csv).")
        return redirect("cliente_list")

    archivo = form.cleaned_data["archivo"]
    try:
        resultado = importar_clientes_desde_archivo(archivo)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("cliente_list")

    creados = resultado["creados"]
    actualizados = resultado["actualizados"]
    errores = resultado["errores"]

    if creados or actualizados:
        messages.success(
            request,
            f"Importación lista: {creados} creado(s), {actualizados} actualizado(s).",
        )
    else:
        messages.warning(request, "No se importó ningún cliente (revisá que haya filas con nombre).")

    if errores:
        detalle = "; ".join(f"fila {f}: {msg}" for f, msg in errores[:5])
        extra = f" (+{len(errores) - 5} más)" if len(errores) > 5 else ""
        messages.warning(request, f"Algunas filas fallaron: {detalle}{extra}")

    return redirect("cliente_list")


@login_required
def exportar_clientes_excel(request):
    clientes = list(clientes_queryset_filtrado(request))
    return exportar_clientes_excel_response(clientes)


@login_required
def exportar_clientes_pdf(request):
    clientes = list(clientes_queryset_filtrado(request))
    return exportar_clientes_pdf_response(clientes)
