from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem
import datetime


WIDGET_CLASS = {'class': 'form-control'}
SELECT_CLASS = {'class': 'form-select'}


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'direccion', 'telefono', 'localidad', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_CLASS, 'required': True, 'placeholder': 'Nombre completo'}),
            'direccion': forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Ej: 358-1234567'}),
            'localidad': forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Ciudad / Localidad'}),
            'email': forms.EmailInput(attrs={**WIDGET_CLASS, 'placeholder': 'correo@ejemplo.com'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono', 'email', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_CLASS, 'required': True}),
            'direccion': forms.TextInput(attrs=WIDGET_CLASS),
            'telefono': forms.TextInput(attrs=WIDGET_CLASS),
            'email': forms.EmailInput(attrs=WIDGET_CLASS),
            'contacto': forms.TextInput(attrs=WIDGET_CLASS),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_unitario', 'stock', 'proveedor', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_CLASS, 'required': True}),
            'descripcion': forms.Textarea(attrs={**WIDGET_CLASS, 'rows': 3}),
            'precio_unitario': forms.NumberInput(attrs={**WIDGET_CLASS, 'step': '0.01', 'min': '0.01'}),
            'stock': forms.NumberInput(attrs={**WIDGET_CLASS, 'min': '0'}),
            'proveedor': forms.Select(attrs=SELECT_CLASS),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['cliente', 'tipo_documento', 'descuento_porcentaje', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs=SELECT_CLASS),
            'tipo_documento': forms.Select(attrs=SELECT_CLASS),
            'descuento_porcentaje': forms.NumberInput(attrs={
                **WIDGET_CLASS, 'step': '0.01', 'min': '0', 'max': '100',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={**WIDGET_CLASS, 'rows': 3}),
        }


class CotizacionItemForm(forms.ModelForm):
    class Meta:
        model = CotizacionItem
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs=SELECT_CLASS),
            'cantidad': forms.NumberInput(attrs={**WIDGET_CLASS, 'min': '1', 'step': '1', 'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={**WIDGET_CLASS, 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True).select_related('proveedor')


# ----- Filtros avanzados -----
class CotizacionFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Número o cliente...'})
    )
    tipo_documento = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Cotizacion.TIPO_DOCUMENTO_CHOICES,
        widget=forms.Select(attrs=SELECT_CLASS)
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados'), ('pendiente', 'Pendiente'), ('completada', 'Completada')],
        widget=forms.Select(attrs=SELECT_CLASS)
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={**WIDGET_CLASS, 'type': 'date'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={**WIDGET_CLASS, 'type': 'date'})
    )


class ProductoFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Nombre o descripción...'})
    )
    proveedor = forms.ModelChoiceField(
        required=False,
        queryset=Proveedor.objects.all(),
        empty_label='Todos los proveedores',
        widget=forms.Select(attrs=SELECT_CLASS)
    )
    activo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos'), ('true', 'Activos'), ('false', 'Inactivos')],
        widget=forms.Select(attrs=SELECT_CLASS)
    )
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={**WIDGET_CLASS, 'placeholder': 'Precio máximo', 'step': '0.01'})
    )


class EnviarEmailForm(forms.Form):
    email_destino = forms.EmailField(
        label="Email del cliente",
        widget=forms.EmailInput(attrs={**WIDGET_CLASS, 'placeholder': 'correo@cliente.com'})
    )
    asunto = forms.CharField(
        label="Asunto",
        widget=forms.TextInput(attrs={**WIDGET_CLASS})
    )
    mensaje = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(attrs={**WIDGET_CLASS, 'rows': 4})
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=WIDGET_CLASS))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=WIDGET_CLASS))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=WIDGET_CLASS))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {'username': forms.TextInput(attrs=WIDGET_CLASS)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(WIDGET_CLASS)
        self.fields['password2'].widget.attrs.update(WIDGET_CLASS)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        from .models import Configuracion
        model = Configuracion
        fields = [
            'ciudad_nombre', 'latitud', 'longitud',
            'empresa_nombre', 'empresa_direccion', 'empresa_telefono', 'empresa_email'
        ]
        widgets = {
            'ciudad_nombre': forms.TextInput(attrs={**WIDGET_CLASS, 'placeholder': 'Ej: Río Cuarto'}),
            'latitud': forms.NumberInput(attrs={**WIDGET_CLASS, 'step': '0.000001'}),
            'longitud': forms.NumberInput(attrs={**WIDGET_CLASS, 'step': '0.000001'}),
            'empresa_nombre': forms.TextInput(attrs=WIDGET_CLASS),
            'empresa_direccion': forms.TextInput(attrs=WIDGET_CLASS),
            'empresa_telefono': forms.TextInput(attrs=WIDGET_CLASS),
            'empresa_email': forms.EmailInput(attrs=WIDGET_CLASS),
        }