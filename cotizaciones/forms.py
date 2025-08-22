from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Proveedor, Producto, Cotizacion, CotizacionItem

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'direccion', 'telefono', 'localidad', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono', 'email', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # Usamos 'precio' que coincide con la columna NOT NULL en la DB
        fields = ['nombre', 'descripcion', 'precio', 'proveedor', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'required': True}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None:
            raise forms.ValidationError("El precio es obligatorio.")
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['numero', 'cliente', 'tipo_documento', 'observaciones']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if len(numero) < 3:
            raise forms.ValidationError("El número debe tener al menos 3 caracteres.")
        return numero

class CotizacionItemForm(forms.ModelForm):
    class Meta:
        model = CotizacionItem
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
