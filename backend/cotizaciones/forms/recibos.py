from django import forms
from ..models.recibos import Recibo, ReciboItem
from ..models.productos import Producto


class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = ["cliente", "fecha", "forma_pago", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "forma_pago": forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"


class ReciboItemForm(forms.ModelForm):
    class Meta:
        model = ReciboItem
        fields = ["producto", "cantidad", "precio_unitario"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1", "value": "1"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.filter(activo=True).select_related("proveedor")
