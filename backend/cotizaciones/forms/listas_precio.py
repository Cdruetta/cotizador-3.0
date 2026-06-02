from django import forms
from ..models.listas_precio import ListaPrecio


class ListaPrecioForm(forms.ModelForm):
    class Meta:
        model = ListaPrecio
        fields = ["nombre", "porcentaje", "por_defecto", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Lista Mayorista"}),
            "porcentaje": forms.NumberInput(attrs={"class": "form-control", "placeholder": "10.00"}),
            "por_defecto": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["porcentaje"].required = False
        for name, field in self.fields.items():
            if name in ("por_defecto", "activo"):
                continue
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"
