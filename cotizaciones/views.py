from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.db import connection, OperationalError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import os
import json
from datetime import date, timedelta
from decimal import Decimal

from .models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem
from .forms import (
    ClienteForm, ProveedorForm, ProductoForm, CotizacionForm,
    CotizacionItemForm, CustomUserCreationForm,
    CotizacionFilterForm, ProductoFilterForm, EnviarEmailForm
)
from .pdf_utils import generar_pdf_cotizacion, generar_pdf_buffer


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def get_db_usage_percent():
    max_size_mb = 100
    engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite3' in engine:
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_mb = os.path.getsize(db_path) / (1024 * 1024)
            return round((db_mb / max_size_mb) * 100, 2), round(db_mb, 2)
        return 0.0, 0.0
    elif 'postgresql' in engine:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database());")
                size_mb = cursor.fetchone()[0] / (1024 * 1024)
                return round((size_mb / max_size_mb) * 100, 2), round(size_mb, 2)
        except OperationalError:
            return 0.0, 0.0
    return 0.0, 0.0


# -------------------------------------------------------
# Dashboard
# -------------------------------------------------------
@login_required
def dashboard(request):
    db_percent, db_mb = get_db_usage_percent()
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    context = {
        'total_clientes': Cliente.objects.count(),
        'total_proveedores': Proveedor.objects.count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_cotizaciones': Cotizacion.objects.count(),
        'cotizaciones_mes': Cotizacion.objects.filter(fecha__gte=inicio_mes).count(),
        'total_facturado_mes': Cotizacion.objects.filter(
            fecha__gte=inicio_mes, completada=True
        ).aggregate(t=Sum('total'))['t'] or Decimal('0'),
        'cotizaciones_pendientes': Cotizacion.objects.filter(completada=False).count(),
        'cotizaciones_recientes': Cotizacion.objects.select_related('cliente', 'usuario')[:5],
        'db_percent': db_percent,
        'db_mb': db_mb,
    }
    return render(request, 'cotizaciones/dashboard.html', context)


# -------------------------------------------------------
# Reportes
# -------------------------------------------------------
@login_required
def reportes(request):
    # Ventas por mes (últimos 6 meses)
    hace_6m = date.today() - timedelta(days=180)
    ventas_mes = (
        Cotizacion.objects.filter(fecha__gte=hace_6m, completada=True)
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('total'), cantidad=Count('id'))
        .order_by('mes')
    )

    # Top 5 clientes por monto
    top_clientes = (
        Cotizacion.objects.filter(completada=True)
        .values('cliente__nombre')
        .annotate(total=Sum('total'), cantidad=Count('id'))
        .order_by('-total')[:5]
    )

    # Top 5 productos más cotizados
    top_productos = (
        CotizacionItem.objects.values('producto__nombre')
        .annotate(veces=Count('id'), total_vendido=Sum('subtotal'))
        .order_by('-veces')[:5]
    )

    # Cotizaciones por estado
    estado_data = {
        'completadas': Cotizacion.objects.filter(completada=True).count(),
        'pendientes': Cotizacion.objects.filter(completada=False).count(),
    }

    # Presupuestos vs recibos
    tipo_data = {
        'presupuestos': Cotizacion.objects.filter(tipo_documento='presupuesto').count(),
        'recibos': Cotizacion.objects.filter(tipo_documento='recibo').count(),
    }

    context = {
        'ventas_mes_json': json.dumps([
            {'mes': v['mes'].strftime('%b %Y'), 'total': float(v['total']), 'cantidad': v['cantidad']}
            for v in ventas_mes
        ]),
        'top_clientes_json': json.dumps([
            {'nombre': c['cliente__nombre'], 'total': float(c['total']), 'cantidad': c['cantidad']}
            for c in top_clientes
        ]),
        'top_productos_json': json.dumps([
            {'nombre': p['producto__nombre'], 'veces': p['veces'], 'total': float(p['total_vendido'])}
            for p in top_productos
        ]),
        'estado_json': json.dumps(estado_data),
        'tipo_json': json.dumps(tipo_data),
        'total_facturado': Cotizacion.objects.filter(completada=True).aggregate(t=Sum('total'))['t'] or 0,
        'promedio_cotizacion': Cotizacion.objects.aggregate(p=Sum('total'))['p'] or 0,
    }
    return render(request, 'cotizaciones/reportes.html', context)


# -------------------------------------------------------
# Usuarios
# -------------------------------------------------------
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'cotizaciones/user_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(username__icontains=search) | Q(first_name__icontains=search) |
                Q(last_name__icontains=search) | Q(email__icontains=search)
            )
        return qs


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'cotizaciones/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)


# -------------------------------------------------------
# Clientes
# -------------------------------------------------------
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'cotizaciones/cliente/list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        qs = Cliente.objects.all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) |
                Q(telefono__icontains=search) |
                Q(localidad__icontains=search)
            )
        return qs


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cotizaciones/cliente/form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado exitosamente.')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cotizaciones/cliente/form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'cotizaciones/cliente/confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cliente eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'cotizaciones/cliente/detail.html'
    context_object_name = 'cliente'


# -------------------------------------------------------
# Proveedores
# -------------------------------------------------------
class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor/list.html'
    context_object_name = 'proveedores'
    paginate_by = 10

    def get_queryset(self):
        qs = Proveedor.objects.all()
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(nombre__icontains=search) | Q(contacto__icontains=search))
        return qs


class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'cotizaciones/proveedor/form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente.')
        return super().form_valid(form)


class ProveedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'cotizaciones/proveedor/form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente.')
        return super().form_valid(form)


class ProveedorDeleteView(LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor/confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ProveedorDetailView(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor/detail.html'
    context_object_name = 'proveedor'


# -------------------------------------------------------
# Productos  (con filtros avanzados)
# -------------------------------------------------------
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'cotizaciones/producto/list.html'
    context_object_name = 'productos'
    paginate_by = 15

    def get_queryset(self):
        qs = Producto.objects.select_related('proveedor')
        form = ProductoFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            proveedor = form.cleaned_data.get('proveedor')
            activo = form.cleaned_data.get('activo')
            precio_max = form.cleaned_data.get('precio_max')
            if search:
                qs = qs.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
            if proveedor:
                qs = qs.filter(proveedor=proveedor)
            if activo == 'true':
                qs = qs.filter(activo=True)
            elif activo == 'false':
                qs = qs.filter(activo=False)
            if precio_max:
                qs = qs.filter(precio_unitario__lte=precio_max)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = ProductoFilterForm(self.request.GET)
        return ctx


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cotizaciones/producto/form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cotizaciones/producto/form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)


class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'cotizaciones/producto/confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = 'cotizaciones/producto/detail.html'
    context_object_name = 'producto'


# -------------------------------------------------------
# Cotizaciones (con filtros avanzados)
# -------------------------------------------------------
class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion/list.html'
    context_object_name = 'cotizaciones'
    paginate_by = 10

    def get_queryset(self):
        qs = Cotizacion.objects.select_related('cliente', 'usuario')
        form = CotizacionFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            tipo = form.cleaned_data.get('tipo_documento')
            estado = form.cleaned_data.get('estado')
            fecha_desde = form.cleaned_data.get('fecha_desde')
            fecha_hasta = form.cleaned_data.get('fecha_hasta')
            if search:
                qs = qs.filter(Q(numero__icontains=search) | Q(cliente__nombre__icontains=search))
            if tipo:
                qs = qs.filter(tipo_documento=tipo)
            if estado == 'pendiente':
                qs = qs.filter(completada=False)
            elif estado == 'completada':
                qs = qs.filter(completada=True)
            if fecha_desde:
                qs = qs.filter(fecha__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha__lte=fecha_hasta)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = CotizacionFilterForm(self.request.GET)
        return ctx


class CotizacionCreateView(LoginRequiredMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion/form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Cotización creada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cotizacion_detail', kwargs={'pk': self.object.pk})


class CotizacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion/form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Recalcular total con nuevo descuento
        self.object.calcular_total()
        messages.success(self.request, 'Cotización actualizada exitosamente.')
        return response

    def get_success_url(self):
        return reverse_lazy('cotizacion_detail', kwargs={'pk': self.object.pk})


class CotizacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion/confirm_delete.html'
    success_url = reverse_lazy('cotizacion_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cotización eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion/detail.html'
    context_object_name = 'cotizacion'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.select_related('producto', 'producto__proveedor')
        ctx['item_form'] = CotizacionItemForm()
        ctx['email_form'] = EnviarEmailForm(initial={
            'email_destino': self.object.cliente.email or '',
            'asunto': f'Cotización {self.object.numero} - GCinsumos',
            'mensaje': f'Estimado/a {self.object.cliente.nombre},\n\nAdjuntamos su cotización. Quedo a disposición.\n\nSaludos,\nGCinsumos'
        })
        return ctx


# -------------------------------------------------------
# Auth
# -------------------------------------------------------
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# -------------------------------------------------------
# API
# -------------------------------------------------------
@login_required
def get_producto_precio(request, producto_id):
    try:
        producto = Producto.objects.select_related('proveedor').get(id=producto_id)
        return JsonResponse({
            'precio': float(producto.precio_unitario),
            'nombre': producto.nombre,
            'proveedor': producto.proveedor.nombre,
            'stock': producto.stock,
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


# -------------------------------------------------------
# Items de cotización
# -------------------------------------------------------
@login_required
def agregar_item_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == 'POST':
        form = CotizacionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.cotizacion = cotizacion
            item.save()
            messages.success(request, 'Producto agregado.')
        else:
            messages.error(request, 'Error al agregar el producto. Verificá los datos.')
    return redirect('cotizacion_detail', pk=cotizacion_id)


@login_required
def eliminar_item_cotizacion(request, item_id):
    item = get_object_or_404(CotizacionItem, id=item_id)
    cotizacion_id = item.cotizacion.id
    item.delete()
    # Recalcular total después de eliminar
    item.cotizacion.calcular_total()
    messages.success(request, 'Producto eliminado.')
    return redirect('cotizacion_detail', pk=cotizacion_id)


# -------------------------------------------------------
# PDF
# -------------------------------------------------------
@login_required
def generar_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return generar_pdf_cotizacion(cotizacion)


# -------------------------------------------------------
# Marcar completada
# -------------------------------------------------------
@login_required
def marcar_cotizacion_completada(request, cotizacion_id):
    if request.method != 'POST':
        return redirect('cotizacion_detail', pk=cotizacion_id)
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    cotizacion.completada = not cotizacion.completada
    cotizacion.save(update_fields=['completada'])
    estado = 'completada' if cotizacion.completada else 'pendiente'
    messages.success(request, f'Cotización marcada como {estado}.')
    return redirect('cotizacion_detail', pk=cotizacion_id)


# -------------------------------------------------------
# Enviar por Email
# -------------------------------------------------------
@login_required
def enviar_cotizacion_email(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == 'POST':
        form = EnviarEmailForm(request.POST)
        if form.is_valid():
            try:
                pdf_buffer = generar_pdf_buffer(cotizacion)
                email = EmailMessage(
                    subject=form.cleaned_data['asunto'],
                    body=form.cleaned_data['mensaje'],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[form.cleaned_data['email_destino']],
                )
                email.attach(
                    f'cotizacion_{cotizacion.numero}.pdf',
                    pdf_buffer.getvalue(),
                    'application/pdf'
                )
                email.send()
                cotizacion.email_enviado = True
                cotizacion.save(update_fields=['email_enviado'])
                messages.success(request, f'Email enviado a {form.cleaned_data["email_destino"]} exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al enviar el email: {str(e)}')
        else:
            messages.error(request, 'Error en el formulario de email.')
    return redirect('cotizacion_detail', pk=cotizacion_id)

# -------------------------------------------------------
# Configuracion del Sistema
# ------------------------------------------------------
@login_required
def configuracion(request):
    if not request.user.is_staff:
        messages.error(request, 'No tenés permiso para acceder a esta página.')
        return redirect('dashboard')

    from .models import Configuracion
    from .forms import ConfiguracionForm
    config = Configuracion.get()

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('configuracion')
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, 'cotizaciones/configuracion.html', {'form': form, 'config': config})