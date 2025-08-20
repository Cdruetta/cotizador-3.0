from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem
from .forms import (
    ClienteForm, ProveedorForm, ProductoForm, CotizacionForm, 
    CotizacionItemForm, CustomUserCreationForm
)
from .pdf_utils import generar_pdf_cotizacion

# Vista principal
@login_required
def dashboard(request):
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_proveedores': Proveedor.objects.count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_cotizaciones': Cotizacion.objects.count(),
        'cotizaciones_recientes': Cotizacion.objects.select_related('cliente')[:5],
    }
    return render(request, 'cotizaciones/dashboard.html', context)

# Vistas para Usuarios
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'cotizaciones/user_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'cotizaciones/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)

# Vistas para Clientes
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'cotizaciones/cliente/list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Cliente.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(telefono__icontains=search) |
                Q(localidad__icontains=search)
            )
        return queryset

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cotizaciones/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado exitosamente.')
        return super().form_valid(form)

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cotizaciones/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado exitosamente.')
        return super().form_valid(form)

class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'cotizaciones/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cliente eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'cotizaciones/cliente_detail.html'
    context_object_name = 'cliente'

# Vistas para Proveedores
class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 10

    def get_queryset(self):
        queryset = Proveedor.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(contacto__icontains=search)
            )
        return queryset

class ProveedorCreateView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'cotizaciones/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente.')
        return super().form_valid(form)

class ProveedorUpdateView(LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'cotizaciones/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente.')
        return super().form_valid(form)

class ProveedorDeleteView(LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ProveedorDetailView(LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'cotizaciones/proveedor_detail.html'
    context_object_name = 'proveedor'

# Vistas para Productos
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'cotizaciones/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Producto.objects.select_related('proveedor')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search) |
                Q(proveedor__nombre__icontains=search)
            )
        return queryset

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cotizaciones/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)

class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'cotizaciones/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)

class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'cotizaciones/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = 'cotizaciones/producto_detail.html'
    context_object_name = 'producto'

# Vistas para Cotizaciones
class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_list.html'
    context_object_name = 'cotizaciones'
    paginate_by = 10

    def get_queryset(self):
        queryset = Cotizacion.objects.select_related('cliente', 'usuario')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) | 
                Q(cliente__nombre__icontains=search)
            )
        return queryset

class CotizacionCreateView(LoginRequiredMixin, CreateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Cotización creada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cotizacion_detail', kwargs={'pk': self.object.pk})

class CotizacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Cotizacion
    form_class = CotizacionForm
    template_name = 'cotizaciones/cotizacion_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Cotización actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cotizacion_detail', kwargs={'pk': self.object.pk})

class CotizacionDeleteView(LoginRequiredMixin, DeleteView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_confirm_delete.html'
    success_url = reverse_lazy('cotizacion_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cotización eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'cotizaciones/cotizacion_detail.html'
    context_object_name = 'cotizacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('producto', 'producto__proveedor')
        context['item_form'] = CotizacionItemForm()
        return context

# Vista para registro de usuarios
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

# API para obtener precio de producto
@login_required
def get_producto_precio(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({
            'precio': float(producto.precio_unitario),
            'nombre': producto.nombre,
            'proveedor': producto.proveedor.nombre
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

# Vista para agregar item a cotización
@login_required
def agregar_item_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    
    if request.method == 'POST':
        form = CotizacionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.cotizacion = cotizacion
            item.save()
            messages.success(request, 'Item agregado exitosamente.')
        else:
            messages.error(request, 'Error al agregar el item.')
    
    return redirect('cotizacion_detail', pk=cotizacion_id)

# Vista para eliminar item de cotización
@login_required
def eliminar_item_cotizacion(request, item_id):
    item = get_object_or_404(CotizacionItem, id=item_id)
    cotizacion_id = item.cotizacion.id
    item.delete()
    messages.success(request, 'Item eliminado exitosamente.')
    return redirect('cotizacion_detail', pk=cotizacion_id)

# Vista para generar PDF
@login_required
def generar_pdf(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    return generar_pdf_cotizacion(cotizacion)
