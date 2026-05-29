from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.views.generic import ListView

from ..models.productos import Producto
from ..models.proveedores import Proveedor
from ..services.productos.export import (
    productos_queryset_filtrado,
    exportar_productos_excel_response,
    exportar_productos_pdf_response,
)
from ..services.productos.import_excel import importar_productos_desde_archivo
from ..forms.productos import ProductoImportForm


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
            messages.error(request, "Seleccioná un archivo válido (.xlsx o .csv).")
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
                f"Importación lista: {creados} creado(s), {actualizados} actualizado(s).",
            )
        else:
            messages.warning(request, "No se importó ningún producto.")

        if errores:
            detalle = "; ".join(f"fila {f}: {msg}" for f, msg in errores[:5])
            extra = f" (+{len(errores) - 5} más)" if len(errores) > 5 else ""
            messages.warning(request, f"Algunas filas fallaron: {detalle}{extra}")

        return redirect("stock_list")

    messages.error(request, "Método no permitido.")
    return redirect("stock_list")
