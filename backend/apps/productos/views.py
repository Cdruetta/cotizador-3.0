from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin

from apps.productos.models import Producto, Categoria, Marca, ListaPrecio, ListaPrecioItem
from apps.productos.forms import ProductoForm, ProductoFilterForm, CategoriaForm, MarcaForm, ListaPrecioForm
from apps.proveedores.models import Proveedor
from cotizaciones.services.productos.export import (
    productos_queryset_filtrado,
    exportar_productos_excel_response,
    exportar_productos_pdf_response,
)
from cotizaciones.services.productos.import_excel import importar_productos_desde_archivo
from cotizaciones.forms.productos import ProductoImportForm


# ============================================
# PRODUCTOS VIEWS
# ============================================

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "cotizaciones/producto/list.html"
    context_object_name = "productos"
    paginate_by = 15

    def get_queryset(self):
        qs = Producto.objects.select_related("proveedor")
        form = ProductoFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get("nombre")
            proveedor = form.cleaned_data.get("proveedor")
            activo = form.cleaned_data.get("activo")
            precio_max = form.cleaned_data.get("precio_max")
            tipo = form.cleaned_data.get("tipo")

            if search:
                qs = qs.filter(
                    Q(nombre__icontains=search) | Q(descripcion__icontains=search)
                )
            if proveedor:
                qs = qs.filter(proveedor__id=proveedor)
            if activo:
                qs = qs.filter(activo=bool(int(activo)))
            if precio_max:
                qs = qs.filter(precio_unitario__lte=precio_max)
            if tipo:
                qs = qs.filter(tipo=tipo)
                
            # Soporte para tipos múltiples
            tipo_multiple = self.request.GET.get('tipo_multiple')
            if tipo_multiple:
                tipos = [t.strip() for t in tipo_multiple.split(',')]
                qs = qs.filter(tipo__in=tipos)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = ProductoFilterForm(self.request.GET)
        # Querystring sin el parámetro de paginación para no duplicar ?page=
        q = self.request.GET.copy()
        q.pop("page", None)
        ctx["current_query"] = q.urlencode()
        # Estadísticas adicionales
        qs = Producto.objects.select_related("proveedor").all()
        ctx["total_stock"] = qs.aggregate(s=Sum("stock"))["s"] or 0
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
        messages.success(self.request, "Producto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = "cotizaciones/producto/detail.html"
    context_object_name = "producto"


# ============================================
# CATEGORIAS VIEWS
# ============================================

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "cotizaciones/categoria/list.html"
    context_object_name = "categorias"
    paginate_by = 10

    def get_queryset(self):
        qs = Categoria.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_categorias"] = Categoria.objects.count()
        ctx["categorias_activas"] = Categoria.objects.filter(activo=True).count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["categorias"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class CategoriaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "cotizaciones/categoria/form.html"
    success_url = reverse_lazy("categoria_list")
    success_message = "Categoría creada correctamente."


class CategoriaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "cotizaciones/categoria/form.html"
    success_url = reverse_lazy("categoria_list")
    success_message = "Categoría actualizada correctamente."


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    success_url = reverse_lazy("categoria_list")
    success_message = "Categoría eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Categoría eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


# ============================================
# MARCAS VIEWS
# ============================================

class MarcaListView(LoginRequiredMixin, ListView):
    model = Marca
    template_name = "cotizaciones/marca/list.html"
    context_object_name = "marcas"
    paginate_by = 10

    def get_queryset(self):
        qs = Marca.objects.all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_marcas"] = Marca.objects.count()
        ctx["marcas_activas"] = Marca.objects.filter(activo=True).count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["marcas"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class MarcaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = "cotizaciones/marca/form.html"
    success_url = reverse_lazy("marca_list")
    success_message = "Marca creada correctamente."


class MarcaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = "cotizaciones/marca/form.html"
    success_url = reverse_lazy("marca_list")
    success_message = "Marca actualizada correctamente."


class MarcaDeleteView(LoginRequiredMixin, DeleteView):
    model = Marca
    success_url = reverse_lazy("marca_list")
    success_message = "Marca eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Marca eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


# ============================================
# LISTAS DE PRECIO VIEWS
# ============================================

class ListaPrecioListView(LoginRequiredMixin, ListView):
    model = ListaPrecio
    template_name = "cotizaciones/listaprecio/list.html"
    context_object_name = "listas"
    paginate_by = 10

    def get_queryset(self):
        qs = ListaPrecio.objects.annotate(cant_items=Count("items")).order_by("nombre")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_listas"] = ListaPrecio.objects.count()
        ctx["listas_activas"] = ListaPrecio.objects.filter(activo=True).count()
        page = ctx.get("page_obj")
        if page and page.paginator.count:
            start = (page.number - 1) * page.paginator.per_page + 1
            ctx["page_start"] = start
            ctx["page_end"] = start + len(ctx["listas"]) - 1
            ctx["page_total"] = page.paginator.count
        else:
            ctx["page_start"] = 0
            ctx["page_end"] = 0
            ctx["page_total"] = 0
        return ctx


class ListaPrecioCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ListaPrecio
    form_class = ListaPrecioForm
    template_name = "cotizaciones/listaprecio/form.html"
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio creada correctamente."


class ListaPrecioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ListaPrecio
    form_class = ListaPrecioForm
    template_name = "cotizaciones/listaprecio/form.html"
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio actualizada correctamente."


class ListaPrecioDeleteView(LoginRequiredMixin, DeleteView):
    model = ListaPrecio
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Lista de precio eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


class ListaPrecioDetailView(LoginRequiredMixin, DetailView):
    model = ListaPrecio
    template_name = "cotizaciones/listaprecio/detail.html"
    context_object_name = "lista"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = self.object.items.select_related().all()
        ctx["items"] = items
        ctx["total_items"] = items.count()
        ctx["categorias"] = list(items.values_list("categoria", flat=True).distinct())
        return ctx


@login_required
def importar_csv_lista_precio(request, pk):
    lista = get_object_or_404(ListaPrecio, pk=pk)

    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        if not archivo.name.endswith(".csv"):
            messages.error(request, "El archivo debe ser .csv")
            return redirect("listaprecio_detail", pk=pk)

        try:
            # Importar las funciones necesarias desde el archivo original
            import csv
            import io
            from datetime import datetime
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            
            def _parsear_precio(valor):
                """Convierte un string de precio a float.
                Ej: '15870' → 15870, '$15.870,50' → 15870.50, '15,870' → 15870.0"""
                import re
                valor = re.sub(r"[^0-9.,\-]", "", valor).strip()
                if not valor:
                    return None
                if "," in valor and "." in valor:
                    valor = valor.replace(".", "").replace(",", ".")
                elif "," in valor:
                    valor = valor.replace(",", ".")
                try:
                    return float(valor)
                except ValueError:
                    return None

            def _detectar_columnas(fieldnames):
                """Busca columnas Categoría, Servicio, Precio (ARS) con variaciones de nombre."""
                lower = [f.strip().lower().replace(" ", "").replace("(", "").replace(")", "").replace("á", "a").replace("í", "i")
                         for f in fieldnames]
                mapa = {}
                for i, name in enumerate(lower):
                    col = fieldnames[i]
                    if name in ("categoria", "categoría", "cat"):
                        mapa["categoria"] = col
                    elif name in ("servicio", "sevicio", "serv"):
                        mapa["servicio"] = col
                    elif "precio" in name and ("ars" in name or "precio" in name):
                        mapa["precio"] = col
                return mapa if {"categoria", "servicio", "precio"}.issubset(mapa) else None

            raw = archivo.read()
            for enc in ("utf-8-sig", "utf-8", "windows-1252", "latin-1"):
                try:
                    decoded = raw.decode(enc)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            else:
                raise UnicodeDecodeError("No se pudo decodificar el archivo con ninguna codificación conocida.")
            col_map = None
            reader = None
            detected_delim = None
            for delim in [",", ";", "\t"]:
                reader = csv.DictReader(io.StringIO(decoded), delimiter=delim)
                col_map = _detectar_columnas([c.strip() for c in reader.fieldnames])
                if col_map:
                    detected_delim = delim
                    break
            if col_map is None:
                messages.error(request, f"Columnas detectadas: {reader.fieldnames if reader else 'ninguna'}")
                return redirect("listaprecio_detail", pk=pk)

            creados = 0
            errores_precio = 0
            for i, row in enumerate(reader, 1):
                categoria = row[col_map["categoria"]].strip()
                servicio = row[col_map["servicio"]].strip()
                precio_raw = row[col_map["precio"]].strip()
                precio_limpio = _parsear_precio(precio_raw)
                if precio_limpio is None:
                    errores_precio += 1
                    continue
                precio = precio_limpio
                ListaPrecioItem.objects.create(
                    lista=lista,
                    categoria=categoria,
                    servicio=servicio,
                    precio=precio,
                )
                creados += 1

            if errores_precio:
                messages.warning(request, f"Se ignoraron {errores_precio} filas con precio inválido.")
            messages.success(request, f"Se importaron {creados} items correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

    return redirect("listaprecio_detail", pk=pk)


@login_required
def agregar_item_lista_precio(request, pk):
    lista = get_object_or_404(ListaPrecio, pk=pk)
    if request.method == "POST":
        categoria = request.POST.get("categoria", "").strip()
        servicio = request.POST.get("servicio", "").strip()
        try:
            precio = float(request.POST.get("precio", 0))
        except ValueError:
            messages.error(request, "Precio inválido.")
            return redirect("listaprecio_detail", pk=pk)
        if not categoria or not servicio:
            messages.error(request, "Categoría y servicio son obligatorios.")
            return redirect("listaprecio_detail", pk=pk)
        ListaPrecioItem.objects.create(lista=lista, categoria=categoria, servicio=servicio, precio=precio)
        messages.success(request, "Item agregado correctamente.")
    return redirect("listaprecio_detail", pk=pk)


@login_required
def editar_item_lista_precio(request, lista_pk, item_pk):
    item = get_object_or_404(ListaPrecioItem, pk=item_pk, lista_id=lista_pk)
    if request.method == "POST":
        item.categoria = request.POST.get("categoria", item.categoria)
        item.servicio = request.POST.get("servicio", item.servicio)
        try:
            item.precio = float(request.POST.get("precio", item.precio))
        except ValueError:
            messages.error(request, "Precio inválido.")
            return redirect("listaprecio_detail", pk=lista_pk)
        item.save()
        messages.success(request, "Item actualizado correctamente.")
    return redirect("listaprecio_detail", pk=lista_pk)


@login_required
def eliminar_item_lista_precio(request, lista_pk, item_pk):
    item = get_object_or_404(ListaPrecioItem, pk=item_pk, lista_id=lista_pk)
    item.delete()
    messages.success(request, "Item eliminado correctamente.")
    return redirect("listaprecio_detail", pk=lista_pk)


@login_required
def exportar_lista_precio_pdf(request, pk):
    lista = get_object_or_404(ListaPrecio.objects.prefetch_related("items"), pk=pk)
    items = lista.items.all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=28, leftMargin=28, topMargin=36, bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TituloLP", parent=styles["Heading1"],
        fontSize=16, textColor=colors.HexColor("#1C3A5E"), spaceAfter=4,
    )
    fecha_txt = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements = [
        Paragraph(lista.nombre, title_style),
        Paragraph(f"<font size=9 color='#64748b'>Generado: {fecha_txt} · {len(items)} items</font>", styles["Normal"]),
        Spacer(1, 12),
    ]

    data = [["Categoría", "Servicio", "Precio (ARS)"]]
    for item in items:
        data.append([item.categoria, item.servicio, f"${float(item.precio):.2f}"])

    if len(data) == 1:
        data.append(["—", "Sin items en esta lista", "—"])

    table = Table(data, colWidths=[1.8 * inch, 3.8 * inch, 1.2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1C3A5E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F9")]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#AACAE6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#AACAE6")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    fecha = datetime.now().strftime("%Y%m%d")
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    slug = lista.nombre.lower().replace(" ", "_")[:30]
    response["Content-Disposition"] = f'attachment; filename="listaprecio_{slug}_{fecha}.pdf"'
    return response


@login_required
def aplicar_precios_lista(request, pk):
    lista = get_object_or_404(ListaPrecio.objects.prefetch_related("items"), pk=pk)
    items = lista.items.all()
    actualizados = 0
    creados = 0

    prov_gcsoft, _ = Proveedor.objects.get_or_create(nombre="GCsoft")
    prov_gcinsumos, _ = Proveedor.objects.get_or_create(nombre="GCinsumos")

    for item in items:
        match = Producto.objects.filter(nombre__iexact=item.servicio).first()
        if match:
            match.precio_unitario = item.precio
            match.save()
            actualizados += 1
        else:
            cat = item.categoria.upper()
            if cat == "HARDWARE":
                proveedor = prov_gcinsumos
                tipo = "servicio_hard"
            else:
                proveedor = prov_gcsoft
                tipo = "servicio_soft"
            Producto.objects.create(
                nombre=item.servicio,
                precio_unitario=item.precio,
                proveedor=proveedor,
                tipo=tipo,
                activo=True,
            )
            creados += 1

    if actualizados:
        messages.success(request, f"Se actualizaron {actualizados} precios de productos existentes.")
    if creados:
        messages.success(request, f"Se crearon {creados} productos nuevos.")

    return redirect("listaprecio_detail", pk=pk)