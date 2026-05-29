from django import forms
from ..models.remitos import Remito, RemitoItem


class RemitoForm(forms.ModelForm):
    class Meta:
        model = Remito
        fields = [
            "cliente",
            "fecha",
            "direccion_entrega",
            "observaciones",
            "estado",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "direccion_entrega": forms.Textarea(attrs={"rows": 2}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }


class RemitoItemForm(forms.ModelForm):
    class Meta:
        model = RemitoItem
        fields = ["producto", "descripcion", "cantidad"]
