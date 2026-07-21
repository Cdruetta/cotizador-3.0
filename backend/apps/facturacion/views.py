import io
import zipfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView

from apps.facturacion.models import ConfiguracionAFIP, Factura, ItemFactura
from apps.ventas.models import Cotizacion
from apps.facturacion.forms import ConfiguracionAFIPForm, GenerarCSRForm, FacturaForm, ItemFacturaForm

from cotizaciones.services.arca.csr import generar_csr
from cotizaciones.services.arca.conexion import probar_conexion, autorizar_factura
from cotizaciones.utils.pdf_utils import generar_pdf_factura


# -- CONFIGURACION AFIP --

@login_required
def configuracion_afip(request):
    config = ConfiguracionAFIP.get_config()
    form = ConfiguracionAFIPForm(request.POST or None, request.FILES or None, instance=config)

    if request.method == 'POST' and 'guardar_config' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuracion actualizada.')
            return redirect('facturacion_config')

    return render(request, 'cotizaciones/facturacion/configuracion.html', {
        'form': form,
        'csr_form': GenerarCSRForm(),
        'config': config,
    })


@login_required
def generar_csr_view(request):
    if request.method != 'POST':
        return redirect('facturacion_config')

    form = GenerarCSRForm(request.POST)
    if form.is_valid():
        clave_pem, csr_pem = generar_csr(form.cleaned_data['cuit'], form.cleaned_data['razon_social'])

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('afip.key', clave_pem)
            zf.writestr('afip.csr', csr_pem)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="certificados_arca.zip"'
        return response
    return redirect('facturacion_config')


@login_required
def test_conexion_afip(request):
    config = ConfiguracionAFIP.get_config()
    if not config:
        messages.error(request, 'Primero completa la configuracion.')
    else:
        ok, msg = probar_conexion(config)
        if ok:
            messages.success(request, f'Conexion exitosa: {msg}')
        else:
            messages.error(request, f'Error de conexion: {msg}')
    return redirect('facturacion_config')


# -- VISTAS DE FACTURA (CRUD) --

class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'cotizaciones/facturacion/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 10
    ordering = ['-id']


class FacturaCreateView(LoginRequiredMixin, CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'cotizaciones/facturacion/factura_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Factura borrador creada.')
        return reverse_lazy('factura_detail', kwargs={'pk': self.object.pk})


class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'cotizaciones/facturacion/factura_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'items': self.object.items.all(),
            'item_form': ItemFacturaForm()
        })
        return context


# -- LOGICA DE NEGOCIO --

@login_required
def agregar_item_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    form = ItemFacturaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.factura = factura
        item.subtotal = item.cantidad * item.precio_unit
        item.save()
        factura.actualizar_totales()
        messages.success(request, 'Item agregado.')

    return redirect('factura_detail', pk=factura_id)


@login_required
@transaction.atomic
def autorizar_factura_view(request, factura_id):
    if request.method != 'POST':
        return redirect('factura_detail', pk=factura_id)

    factura = get_object_or_404(Factura, id=factura_id, estado='borrador')
    config = ConfiguracionAFIP.get_config()

    if not config:
        messages.error(request, 'Debe configurar los certificados AFIP primero.')
        return redirect('facturacion_config')

    ok, msg = autorizar_factura(config, factura)
    if ok:
        messages.success(request, "Factura autorizada con exito!")
    else:
        messages.error(request, f'Error de AFIP: {msg}')

    return redirect('factura_detail', pk=factura_id)


@login_required
def generar_pdf_factura_view(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return generar_pdf_factura(factura)


@login_required
def crear_factura_desde_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    with transaction.atomic():
        factura = Factura.objects.create(
            cliente=cotizacion.cliente,
            punto_venta=1,
            usuario=request.user,
        )

        items_factura = []
        for item in cotizacion.items.select_related("producto").all():
            items_factura.append(
                ItemFactura(
                    factura=factura,
                    descripcion=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_unit=item.precio_unitario,
                    subtotal=item.cantidad * item.precio_unitario,
                )
            )

        ItemFactura.objects.bulk_create(items_factura)
        factura.actualizar_totales()

    messages.success(request, f"Factura generada desde Cotizacion N {cotizacion.numero}")
    return redirect("factura_detail", pk=factura.pk)
