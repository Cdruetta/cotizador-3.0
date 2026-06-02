from django import forms
from ..models.tienda_web import TiendaWebConfig


class TiendaWebConfigForm(forms.ModelForm):
    class Meta:
        model = TiendaWebConfig
        fields = ["activa", "nombre_tienda", "descripcion", "email_contacto"]
        widgets = {
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "nombre_tienda": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Mi Tienda"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción de la tienda"}),
            "email_contacto": forms.EmailInput(attrs={"class": "form-control", "placeholder": "tienda@ejemplo.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "activa":
                continue
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"
