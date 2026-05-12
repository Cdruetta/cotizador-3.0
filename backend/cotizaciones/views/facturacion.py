import io, zipfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy

from ..models import ConfiguracionAFIP, Factura, ItemFactura
from ..forms.facturacion import ConfiguracionAFIPForm, GenerarCSRForm, FacturaForm, ItemFacturaForm
from ..services.arca.csr import generar_csr
from ..services.arca.conexion import probar_conexion, autorizar_factura
from ..utils.pdf_utils import generar_pdf_factura


# ── Configuración ────────────────────────────────────────────


@login_required
def configuracion_afip(request):
    config = ConfiguracionAFIP.get_config()
    form = ConfiguracionAFIPForm(request.POST or None, request.FILES or None, instance=config)
    csr_form = GenerarCSRForm()

    if request.method == 'POST' and 'guardar_config' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('facturacion_config')

    return render(request, 'cotizaciones/facturacion/configuracion.html', {
        'form': form,
        'csr_form': csr_form,
        'config': config,
    })


@login_required
def generar_csr_view(request):
    if request.method == 'POST':
        form = GenerarCSRForm(request.POST)
        if form.is_valid():
            clave_pem, csr_pem = generar_csr(
                form.cleaned_data['cuit'],
                form.cleaned_data['razon_social']
            )
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
    if not config or not config.certificado or not config.clave_privada:
        messages.error(request, 'Primero completá la configuración y subí los certificados.')
    else:
        ok, msg = probar_conexion(config)
        if ok:
            messages.success(request, msg)
        else:
            messages.error(request, f'Error: {msg}')
    return redirect('facturacion_config')


# ── Facturas ─────────────────────────────────────────────────

class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'cotizaciones/facturacion/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 10


class FacturaCreateView(LoginRequiredMixin, CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'cotizaciones/facturacion/factura_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Factura creada. Agregá los ítems y luego autorizala.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('factura_detail', kwargs={'pk': self.object.pk})


class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'cotizaciones/facturacion/factura_detail.html'
    context_object_name = 'factura'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.all()
        ctx['item_form'] = ItemFacturaForm()
        return ctx


@login_required
def agregar_item_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    if request.method == 'POST':
        form = ItemFacturaForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.factura = factura
            item.save()
            # Recalcular total
            factura.total = sum(i.subtotal for i in factura.items.all())
            factura.neto = factura.total
            factura.save(update_fields=['total', 'neto'])
            messages.success(request, 'Ítem agregado.')
        else:
            messages.error(request, 'Error al agregar el ítem.')
    return redirect('factura_detail', pk=factura_id)


@login_required
def autorizar_factura_view(request, factura_id):
    if request.method != 'POST':
        return redirect('factura_detail', pk=factura_id)
    factura = get_object_or_404(Factura, id=factura_id, estado='borrador')
    config = ConfiguracionAFIP.get_config()
    if not config:
        messages.error(request, 'No hay configuración ARCA. Configurá primero.')
        return redirect('factura_detail', pk=factura_id)
    ok, msg = autorizar_factura(config, factura)
    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, f'Error ARCA: {msg}')
    return redirect('factura_detail', pk=factura_id)


@login_required
def generar_pdf_factura_view(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return generar_pdf_factura(factura)

