import csv
import io
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from ..models.listas_precio import ListaPrecio, ListaPrecioItem
from ..models.productos import Producto
from ..models.proveedores import Proveedor
from ..forms.listas_precio import ListaPrecioForm


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ListaPrecioListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
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


class ListaPrecioCreateView(LoginRequiredMixin, StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = ListaPrecio
    form_class = ListaPrecioForm
    template_name = "cotizaciones/listaprecio/form.html"
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio creada correctamente."


class ListaPrecioUpdateView(LoginRequiredMixin, StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ListaPrecio
    form_class = ListaPrecioForm
    template_name = "cotizaciones/listaprecio/form.html"
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio actualizada correctamente."


class ListaPrecioDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ListaPrecio
    success_url = reverse_lazy("listaprecio_list")
    success_message = "Lista de precio eliminada correctamente."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ListaPrecioDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
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


def importar_csv_lista_precio(request, pk):
    lista = get_object_or_404(ListaPrecio, pk=pk)

    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        if not archivo.name.endswith(".csv"):
            messages.error(request, "El archivo debe ser .csv")
            return redirect("listaprecio_detail", pk=pk)

        try:
            raw = archivo.read()
            for enc in ("utf-8-sig", "utf-8", "windows-1252", "latin-1"):
                try:
                    decoded = raw.decode(enc)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            else:
                raise UnicodeDecodeError("No se pudo decodificar el archivo con ninguna codificación conocida.")
            reader = csv.DictReader(io.StringIO(decoded))
            required = {"Categoría", "Servicio", "Precio (ARS)"}
            if not required.issubset(reader.fieldnames):
                messages.error(request, f"El CSV debe tener las columnas: {', '.join(sorted(required))}")
                return redirect("listaprecio_detail", pk=pk)

            creados = 0
            for row in reader:
                categoria = row["Categoría"].strip()
                servicio = row["Servicio"].strip()
                precio_raw = row["Precio (ARS)"].replace(".", "").replace(",", ".").strip()
                try:
                    precio = float(precio_raw)
                except ValueError:
                    continue
                ListaPrecioItem.objects.create(
                    lista=lista,
                    categoria=categoria,
                    servicio=servicio,
                    precio=precio,
                )
                creados += 1

            messages.success(request, f"Se importaron {creados} items correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

    return redirect("listaprecio_detail", pk=pk)


@login_required
def agregar_item_lista_precio(request, pk):
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso.")
        return redirect("listaprecio_detail", pk=pk)
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
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso.")
        return redirect("listaprecio_detail", pk=lista_pk)
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
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso.")
        return redirect("listaprecio_detail", pk=lista_pk)
    item = get_object_or_404(ListaPrecioItem, pk=item_pk, lista_id=lista_pk)
    item.delete()
    messages.success(request, "Item eliminado correctamente.")
    return redirect("listaprecio_detail", pk=lista_pk)


@login_required
def exportar_lista_precio_pdf(request, pk):
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso.")
        return redirect("listaprecio_list")

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
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso.")
        return redirect("listaprecio_list")

    lista = get_object_or_404(ListaPrecio.objects.prefetch_related("items"), pk=pk)
    items = lista.items.all()
    actualizados = 0
    creados = 0

    proveedor_default, _ = Proveedor.objects.get_or_create(
        nombre="Servicios",
    )

    for item in items:
        match = Producto.objects.filter(nombre__iexact=item.servicio).first()
        if match:
            match.precio_unitario = item.precio
            match.save()
            actualizados += 1
        else:
            tipo = "servicio_hard" if item.categoria.upper() == "HARDWARE" else "servicio_soft"
            Producto.objects.create(
                nombre=item.servicio,
                precio_unitario=item.precio,
                proveedor=proveedor_default,
                tipo=tipo,
                activo=True,
            )
            creados += 1

    if actualizados:
        messages.success(request, f"Se actualizaron {actualizados} precios de productos existentes.")
    if creados:
        messages.success(request, f"Se crearon {creados} productos nuevos.")

    return redirect("listaprecio_detail", pk=pk)
