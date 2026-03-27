from django import forms

from ..models import Producto, Proveedor
from .common import WIDGET_CLASS, SELECT_CLASS


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "tipo", "precio_unitario", "stock", "proveedor", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={**WIDGET_CLASS, "required": True}),
            "descripcion": forms.Textarea(attrs={**WIDGET_CLASS, "rows": 3}),
            "tipo": forms.Select(attrs=SELECT_CLASS),
            "precio_unitario": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.01", "min": "0.01"}),
            "stock": forms.NumberInput(attrs={**WIDGET_CLASS, "min": "0"}),
            "proveedor": forms.Select(attrs=SELECT_CLASS),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get("precio_unitario")
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio


class ProductoFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Nombre o descripción..."}),
    )
    proveedor = forms.ModelChoiceField(
        required=False,
        queryset=Proveedor.objects.all(),
        empty_label="Todos los proveedores",
        widget=forms.Select(attrs=SELECT_CLASS),
    )
    activo = forms.ChoiceField(
        required=False,
        choices=[("", "Todos"), ("true", "Activos"), ("false", "Inactivos")],
        widget=forms.Select(attrs=SELECT_CLASS),
    )
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={**WIDGET_CLASS, "placeholder": "Precio máximo", "step": "0.01"}),
    )

    tipo = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los tipos")] + list(Producto.TIPO_CHOICES),
        widget=forms.Select(attrs=SELECT_CLASS),
    )

