from django import forms

from ..models import Cliente
from .common import WIDGET_CLASS


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "direccion", "telefono", "localidad", "email", "activo"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={**WIDGET_CLASS, "required": True, "placeholder": "Nombre completo"}
            ),
            "direccion": forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Dirección"}),
            "telefono": forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Ej: 358-1234567"}),
            "localidad": forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Ciudad / Localidad"}),
            "email": forms.EmailInput(attrs={**WIDGET_CLASS, "placeholder": "correo@ejemplo.com"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ClienteImportForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel o CSV",
        help_text="Columnas: nombre (obligatorio), email, teléfono, dirección, localidad, activo.",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".xlsx,.csv"}),
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

