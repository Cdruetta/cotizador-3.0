from django import forms

from ..models import Configuracion
from .common import WIDGET_CLASS


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            "ciudad_nombre",
            "latitud",
            "longitud",
            "empresa_nombre",
            "empresa_direccion",
            "empresa_telefono",
            "empresa_email",
        ]
        widgets = {
            "ciudad_nombre": forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Ej: Río Cuarto"}),
            "latitud": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.000001"}),
            "longitud": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.000001"}),
            "empresa_nombre": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_direccion": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_telefono": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_email": forms.EmailInput(attrs=WIDGET_CLASS),
        }

