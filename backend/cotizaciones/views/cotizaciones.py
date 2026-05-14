from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from ..forms import (
    CotizacionForm,
    CotizacionItemForm,
    CotizacionFilterForm,
    EnviarEmailForm,
)

from ..models import Cotizacion, CotizacionItem

from ..services.communication.email import (
    enviar_cotizacion_por_email,
)

from ..services.documents.pdf import (
    build_cotizacion_pdf_response,
)


# =========================
# LISTADO
# =========================
class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = "cotizaciones/cotizacion/list.html"
    context_object_name = "cotizaciones"
    paginate_by = 10

    def get_queryset(self):
        qs = Cotizacion.objects.select_related("cliente", "usuario")
        form = CotizacionFilterForm(self.request.GET)

        if form.is_valid():
            search = form.cleaned_data.get("search")
            tipo = form.cleaned_data.get("tipo_documento")
            estado = form.cleaned_data.get("estado")
            fecha_desde = form.cleaned_data.get("fecha_desde")
            fecha_hasta = form.cleaned_data.get("fecha_hasta")

            if search:
                qs = qs.filter(
                    Q(numero__icontains=search)
                    | Q(cliente__nombre__icontains=search)
                )

            if tipo:
                qs = qs.filter(tipo_documento=tipo)

            if estado:
                qs = qs.filter(estado=estado)

            if fecha_desde:
                qs = qs.filter(fecha__gte=fecha_desde)

            if fecha_hasta:
                qs = qs.filter(fecha__lte=fecha_hasta)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = CotizacionFilterForm(self.request.GET)
        return ctx


# =========================
# CREAR
# =========================
class CotizacionCreateView(LoginRequiredMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = "cotizaciones/cotizacion/form.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Cotización creada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("cotizacion_detail", kwargs={"pk": self.object.pk})


# =========================
# EDITAR
# =========================
class CotizacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = "cotizaciones/cotizacion/form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.calcular_total()
        messages.success(self.request, "Cotización actualizada exitosamente.")
        return response

    def get_success_url(self):
        return reverse_lazy("cotizacion_detail", kwargs={"pk": self.object.pk})


# =========================
# ELIMINAR
# =========================
class CotizacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Cotizacion
    template_name = "cotizaciones/cotizacion/confirm_delete.html"
    success_url = reverse_lazy("cotizacion_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cotización eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# =========================
# DETALLE
# =========================
class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = "cotizaciones/cotizacion/detail.html"
    context_object_name = "cotizacion"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = self.object.items.select_related(
            "producto",
            "producto__proveedor",
        )
        ctx["item_form"] = CotizacionItemForm()
        ctx["factura_creada_pk"] = None
        ctx["email_form"] = EnviarEmailForm(
            initial={
                "email_destino": self.object.cliente.email or "",
                "asunto": f"Cotización {self.object.numero} - GCinsumos",
                "mensaje": (
                    f"Estimado/a {self.object.cliente.nombre},\n\n"
                    "Adjuntamos su cotización.\n\n"
                    "Quedamos a disposición.\n\n"
                    "Saludos,\n"
                    "GCinsumos"
                ),
            }
        )
        return ctx


# =========================
# AGREGAR ITEM
# =========================
@login_required
def agregar_item_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == "POST":
        form = CotizacionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.cotizacion = cotizacion
            item.save()
            messages.success(request, "Producto agregado.")
        else:
            messages.error(request, "Error al agregar el producto.")
    return redirect("cotizacion_detail", pk=cotizacion_id)


# =========================
# ELIMINAR ITEM
# =========================
@login_required
def eliminar_item_cotizacion(request, item_id):
    item = get_object_or_404(CotizacionItem, id=item_id)
    cotizacion_id = item.cotizacion.id
    item.delete()
    item.cotizacion.calcular_total()
    messages.success(request, "Producto eliminado.")
    return redirect("cotizacion_detail", pk=cotizacion_id)


# =========================
# PDF
# =========================
@login_required
def generar_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return build_cotizacion_pdf_response(cotizacion=cotizacion)


# =========================
# CAMBIO DE ESTADO (OPTIMIZADO)
# =========================
@login_required
def cambiar_estado_cotizacion(request, cotizacion_id, estado):
    """
    Cambia el estado de una cotización y redirige dinámicamente a la página de origen
    (Dashboard, Lista o Detalle) para evitar interrupciones en el flujo de trabajo.
    """
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    estados_validos = [e[0] for e in Cotizacion.ESTADO_CHOICES]

    if estado not in estados_validos:
        messages.error(request, "Estado inválido.")
        return redirect("cotizacion_detail", pk=cotizacion_id)

    cotizacion.estado = estado
    cotizacion.save(update_fields=["estado"])

    messages.success(
        request,
        f"Cotización {cotizacion.numero} actualizada a {cotizacion.get_estado_display()}."
    )

    # Lógica de redirección dinámica:
    # 1. Intenta volver a la URL anterior (HTTP_REFERER)
    # 2. Si no existe o falla, redirige al detalle de la cotización por defecto
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    
    return redirect("cotizacion_detail", pk=cotizacion_id)


# =========================
# ENVIAR EMAIL
# =========================
@login_required
def enviar_cotizacion_email(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == "POST":
        form = EnviarEmailForm(request.POST)
        if form.is_valid():
            try:
                enviar_cotizacion_por_email(
                    cotizacion=cotizacion,
                    email_destino=form.cleaned_data["email_destino"],
                    asunto=form.cleaned_data["asunto"],
                    mensaje=form.cleaned_data["mensaje"],
                )
                cotizacion.email_enviado = True
                cotizacion.save(update_fields=["email_enviado"])
                messages.success(
                    request,
                    f'Email enviado a {form.cleaned_data["email_destino"]} exitosamente.'
                )
            except Exception as e:
                messages.error(request, f"Error al enviar el email: {str(e)}")
        else:
            messages.error(request, "Error en el formulario de email.")
    return redirect("cotizacion_detail", pk=cotizacion_id)