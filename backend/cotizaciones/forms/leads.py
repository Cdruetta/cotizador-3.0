from django import forms
from ..models.leads import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "nombre",
            "email",
            "telefono",
            "empresa",
            "cargo",
            "estado",
            "fuente",
            "notas",
            "asignado_a",
            "activo",
        ]
        widgets = {
            "notas": forms.Textarea(attrs={"rows": 3}),
        }
