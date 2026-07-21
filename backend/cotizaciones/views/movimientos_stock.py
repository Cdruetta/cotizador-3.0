from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.messages.views import SuccessMessageMixin

from ..models import MovimientoStock
from ..models import Producto
from ..forms.movimientos_stock import MovimientoStockForm


class MovimientoStockListView(LoginRequiredMixin, ListView):
    model = MovimientoStock
    template_name = "cotizaciones/movimiento_stock/list.html"
    context_object_name = "movimientos"
    paginate_by = 15

    def get_queryset(self):
        qs = MovimientoStock.objects.select_related("producto", "usuario")
        producto_id = self.request.GET.get("producto")
        tipo = self.request.GET.get("tipo")
        if producto_id:
            qs = qs.filter(producto_id=producto_id)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["movimientos"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        ctx["total_movimientos"] = MovimientoStock.objects.count()
        ctx["total_entradas"] = MovimientoStock.objects.filter(tipo="entrada").count()
        ctx["total_salidas"] = MovimientoStock.objects.filter(tipo="salida").count()
        ctx["filtro_tipo"] = self.request.GET.get("tipo", "")
        ctx["productos"] = Producto.objects.filter(activo=True)
        ctx["filtro_producto"] = self.request.GET.get("producto", "")
        return ctx


class MovimientoStockCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MovimientoStock
    form_class = MovimientoStockForm
    template_name = "cotizaciones/movimiento_stock/form.html"
    success_url = reverse_lazy("movimiento_stock_list")
    success_message = "Movimiento registrado correctamente."

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        movimiento = form.save(commit=False)
        producto = movimiento.producto
        if movimiento.tipo == "entrada":
            producto.stock += movimiento.cantidad
        elif movimiento.tipo == "salida":
            if producto.stock < movimiento.cantidad:
                form.add_error("cantidad", "Stock insuficiente para esta salida.")
                return self.form_invalid(form)
            producto.stock -= movimiento.cantidad
        else:  # ajuste
            producto.stock = movimiento.cantidad
        movimiento.stock_resultante = producto.stock
        producto.save()
        movimiento.save()
        return super().form_valid(form)
