from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin

from ..models.recibos import Recibo, ReciboItem
from ..forms.recibos import ReciboForm, ReciboItemForm
from ..forms.cotizaciones import EnviarEmailForm
from ..services.recibos import recibo_queryset_filtrado
from ..services.documents.pdf import build_recibo_pdf_response
from ..services.communication.email import enviar_recibo_por_email


class ReciboListView(LoginRequiredMixin, ListView):
    model = Recibo
    template_name = "cotizaciones/recibo/list.html"
    context_object_name = "recibos"
    paginate_by = 10

    def get_queryset(self):
        qs = recibo_queryset_filtrado(self.request.user)
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            qs = qs.filter(numero__icontains=busqueda) | qs.filter(cliente__nombre__icontains=busqueda)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["recibos"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        ctx["total_recibos"] = Recibo.objects.count()
        return ctx


class ReciboCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Recibo
    form_class = ReciboForm
    template_name = "cotizaciones/recibo/form.html"
    success_message = "Recibo creado correctamente."

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("recibo_detail", kwargs={"pk": self.object.pk})


class ReciboUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Recibo
    form_class = ReciboForm
    template_name = "cotizaciones/recibo/form.html"
    success_message = "Recibo actualizado correctamente."

    def get_success_url(self):
        return reverse_lazy("recibo_detail", kwargs={"pk": self.object.pk})


class ReciboDeleteView(LoginRequiredMixin, DeleteView):
    model = Recibo
    success_url = reverse_lazy("recibo_list")
    success_message = "Recibo eliminado correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ReciboDetailView(LoginRequiredMixin, DetailView):
    model = Recibo
    template_name = "cotizaciones/recibo/detail.html"
    context_object_name = "recibo"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = self.object.items.select_related("producto")
        ctx["item_form"] = ReciboItemForm()
        cliente_nombre = getattr(self.object.cliente, 'razon_social', getattr(self.object.cliente, 'nombre', 'Cliente'))
        ctx["email_form"] = EnviarEmailForm(
            initial={
                "email_destino": self.object.cliente.email or "",
                "asunto": f"Recibo {self.object.numero} - GCinsumos",
                "mensaje": f"Estimado/a {cliente_nombre},\n\nAdjuntamos su recibo.\n\nSaludos,\nGCinsumos",
            }
        )
        return ctx


@login_required
def agregar_item_recibo(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    if request.method == "POST":
        form = ReciboItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.recibo = recibo
            item.save()
            recibo.actualizar_totales()
            messages.success(request, "Producto agregado.")
    return redirect("recibo_detail", pk=recibo_id)


@login_required
def eliminar_item_recibo(request, item_id):
    item = get_object_or_404(ReciboItem, id=item_id)
    recibo_id = item.recibo.id
    item.delete()
    item.recibo.actualizar_totales()
    messages.success(request, "Producto eliminado.")
    return redirect("recibo_detail", pk=recibo_id)


@login_required
def generar_pdf_recibo(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    return build_recibo_pdf_response(recibo=recibo)


@login_required
def enviar_recibo_email(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    if request.method == "POST":
        form = EnviarEmailForm(request.POST)
        if form.is_valid():
            try:
                enviar_recibo_por_email(
                    recibo=recibo,
                    email_destino=form.cleaned_data["email_destino"],
                    asunto=form.cleaned_data["asunto"],
                    mensaje=form.cleaned_data["mensaje"],
                )
                messages.success(request, "Email enviado con éxito.")
            except Exception as e:
                messages.error(request, f"Error al enviar: {str(e)}")
    return redirect("recibo_detail", pk=recibo_id)
