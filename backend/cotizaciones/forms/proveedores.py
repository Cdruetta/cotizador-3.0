from django import forms

from ..models import Proveedor
from .common import WIDGET_CLASS


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "direccion", "telefono", "email", "contacto"]
        widgets = {
            "nombre": forms.TextInput(attrs={**WIDGET_CLASS, "required": True}),
            "direccion": forms.TextInput(attrs=WIDGET_CLASS),
            "telefono": forms.TextInput(attrs=WIDGET_CLASS),
            "email": forms.EmailInput(attrs=WIDGET_CLASS),
            "contacto": forms.TextInput(attrs=WIDGET_CLASS),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

