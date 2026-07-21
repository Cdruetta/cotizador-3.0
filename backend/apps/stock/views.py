from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.contrib.messages.views import SuccessMessageMixin

from apps.productos.models import Producto, Proveedor
from apps.stock.models import MovimientoStock
from cotizaciones.services.productos.export import (
    productos_queryset_filtrado,
    exportar_productos_excel_response,
    exportar_productos_pdf_response,
)
from cotizaciones.services.productos.import_excel import importar_productos_desde_archivo
from apps.productos.forms import ProductoImportForm
from apps.stock.forms import MovimientoStockForm


class StockListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "cotizaciones/stock/list.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        qs = Producto.objects.select_related("proveedor").all()
        q = self.request.GET.get("q", "").strip()
        proveedor_id = self.request.GET.get("proveedor")
        activo = self.request.GET.get("activo")
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        if proveedor_id:
            qs = qs.filter(proveedor_id=proveedor_id)
        if activo == "1":
            qs = qs.filter(activo=True)
        elif activo == "0":
            qs = qs.filter(activo=False)
        return qs.order_by("nombre")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["productos"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        base = Producto.objects
        ctx["total_productos"] = base.count()
        ctx["total_stock"] = base.aggregate(s=Sum("stock"))["s"] or 0
        ctx["sin_stock"] = base.filter(stock=0).count()
        ctx["proveedores"] = Proveedor.objects.all()
        ctx["filtro_q"] = self.request.GET.get("q", "")
        ctx["filtro_proveedor"] = self.request.GET.get("proveedor", "")
        ctx["filtro_activo"] = self.request.GET.get("activo", "")
        return ctx


@login_required
def exportar_stock_excel(request):
    productos = list(productos_queryset_filtrado(request))
    return exportar_productos_excel_response(productos)


@login_required
def exportar_stock_pdf(request):
    productos = list(productos_queryset_filtrado(request))
    return exportar_productos_pdf_response(productos)


@login_required
def importar_stock_excel(request):
    if request.method == "POST":
        form = ProductoImportForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Selecciona un archivo valido (.xlsx o .csv).")
            return redirect("stock_list")

        archivo = form.cleaned_data["archivo"]
        try:
            resultado = importar_productos_desde_archivo(archivo)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("stock_list")

        creados = resultado["creados"]
        actualizados = resultado["actualizados"]
        errores = resultado["errores"]

        if creados or actualizados:
            messages.success(
                request,
                f"Importacion lista: {creados} creado(s), {actualizados} actualizado(s).",
            )
        else:
            messages.warning(request, "No se importo ningun producto.")

        if errores:
            detalle = "; ".join(f"fila {f}: {msg}" for f, msg in errores[:5])
            extra = f" (+{len(errores) - 5} mas)" if len(errores) > 5 else ""
            messages.warning(request, f"Algunas filas fallaron: {detalle}{extra}")

        return redirect("stock_list")

    messages.error(request, "Metodo no permitido.")
    return redirect("stock_list")


# Movimientos de stock

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
