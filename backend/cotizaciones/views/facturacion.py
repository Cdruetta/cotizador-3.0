import io, zipfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.db import transaction

from ..models import ConfiguracionAFIP, Factura, ItemFactura, Cotizacion
from ..forms.facturacion import ConfiguracionAFIPForm, GenerarCSRForm, FacturaForm, ItemFacturaForm

from ..services.arca.csr import generar_csr
from ..services.arca.conexion import probar_conexion, autorizar_factura
from ..utils.pdf_utils import generar_pdf_factura

# ── CONFIGURACIÓN AFIP ────────────────────────────────────────

@login_required
def configuracion_afip(request):
    """Gestión de certificados y datos fiscales para ARCA."""
    config = ConfiguracionAFIP.get_config()
    form = ConfiguracionAFIPForm(request.POST or None, request.FILES or None, instance=config)
    
    if request.method == 'POST' and 'guardar_config' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada.')
            return redirect('facturacion_config')

    return render(request, 'cotizaciones/facturacion/configuracion.html', {
        'form': form,
        'csr_form': GenerarCSRForm(),
        'config': config,
    })

@login_required
def generar_csr_view(request):
    """Genera la clave privada y el pedido de certificado (CSR)."""
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
    """Prueba la comunicación con los servidores de AFIP."""
    config = ConfiguracionAFIP.get_config()
    if not config or not config.certificado or not config.clave_privada:
        messages.error(request, 'Primero completá la configuración y subí los certificados.')
    else:
        ok, msg = probar_conexion(config)
        if ok:
            messages.success(request, f'Conexión exitosa: {msg}')
        else:
            messages.error(request, f'Error de conexión: {msg}')
    return redirect('facturacion_config')

# ── VISTAS DE FACTURA (CRUD) ──────────────────────────────────

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

# ── LÓGICA DE NEGOCIO ─────────────────────────────────────────

@login_required
def agregar_item_factura(request, factura_id):
    """Añade un ítem manualmente a una factura existente."""
    factura = get_object_or_404(Factura, id=factura_id)
    form = ItemFacturaForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.factura = factura
        # Calculamos subtotal antes de guardar por seguridad
        item.subtotal = item.cantidad * item.precio_unit
        item.save()
        
        factura.actualizar_totales() 
        messages.success(request, 'Ítem añadido.')
        
    return redirect('factura_detail', pk=factura_id)

@login_required
@transaction.atomic 
def autorizar_factura_view(request, factura_id):
    """Envía la factura a AFIP para obtener el CAE."""
    if request.method != 'POST':
        return redirect('factura_detail', pk=factura_id)
        
    factura = get_object_or_404(Factura, id=factura_id, estado='borrador')
    config = ConfiguracionAFIP.get_config()
    
    if not config:
        messages.error(request, 'Debe configurar los certificados AFIP primero.')
        return redirect('facturacion_config')

    ok, msg = autorizar_factura(config, factura)
    if ok:
        messages.success(request, "¡Factura autorizada con éxito!")
    else:
        messages.error(request, f'Error de AFIP: {msg}')
        
    return redirect('factura_detail', pk=factura_id)

@login_required
def generar_pdf_factura_view(request, factura_id):
    """Muestra el PDF de la factura."""
    factura = get_object_or_404(Factura, id=factura_id)
    return generar_pdf_factura(factura)

@login_required
def crear_factura_desde_cotizacion(request, cotizacion_id):
    """Convierte una cotización existente en una factura borrador."""
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    with transaction.atomic():
        # 1. Crear la Factura
        factura = Factura.objects.create(
            cliente=cotizacion.cliente,
            punto_venta=1,
            usuario=request.user,
        )

        # 2. Mapear ítems de cotización a ítems de factura
        # Se calcula el subtotal aquí para evitar IntegrityError (NOT NULL)
        items_factura = []
        for item in cotizacion.items.select_related("producto").all():
            items_factura.append(
                ItemFactura(
                    factura=factura,
                    descripcion=item.producto.nombre,
                    cantidad=item.cantidad,
                    precio_unit=item.precio_unitario,
                    subtotal=item.cantidad * item.precio_unitario # <--- FIX
                )
            )
        
        # Inserción masiva eficiente
        ItemFactura.objects.bulk_create(items_factura)

        # 3. Refrescar totales de la factura
        factura.actualizar_totales()

    messages.success(request, f"Factura generada desde Cotización N° {cotizacion.numero}")
    return redirect("factura_detail", pk=factura.pk)