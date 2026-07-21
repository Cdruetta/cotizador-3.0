from django import forms

from .models import Cotizacion, CotizacionItem, Recibo, ReciboItem, Remito, RemitoItem
from apps.core.forms import WIDGET_CLASS, SELECT_CLASS
from apps.productos.models import Producto


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ["cliente", "tipo_documento", "observaciones"]
        widgets = {
            "cliente": forms.Select(attrs=SELECT_CLASS),
            "tipo_documento": forms.Select(attrs=SELECT_CLASS),
            "observaciones": forms.Textarea(attrs={**WIDGET_CLASS, "rows": 3}),
        }


class CotizacionItemForm(forms.ModelForm):
    class Meta:
        model = CotizacionItem
        fields = ["producto", "cantidad", "precio_unitario"]
        widgets = {
            "producto": forms.Select(attrs=SELECT_CLASS),
            "cantidad": forms.NumberInput(attrs={**WIDGET_CLASS, "min": "1", "step": "1", "value": "1"}),
            "precio_unitario": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.01", "min": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.filter(activo=True).select_related("proveedor")


class CotizacionFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Número o cliente..."}),
    )
    tipo_documento = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los tipos")] + Cotizacion.TIPO_CHOICES,
        widget=forms.Select(attrs=SELECT_CLASS),
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los estados")] + Cotizacion.ESTADO_CHOICES,
        widget=forms.Select(attrs=SELECT_CLASS),
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={**WIDGET_CLASS, "type": "date"}),
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={**WIDGET_CLASS, "type": "date"}),
    )


class EnviarEmailForm(forms.Form):
    email_destino = forms.EmailField(
        label="Email del cliente",
        widget=forms.EmailInput(attrs={**WIDGET_CLASS, "placeholder": "correo@cliente.com"}),
    )
    asunto = forms.CharField(
        label="Asunto",
        widget=forms.TextInput(attrs={**WIDGET_CLASS}),
    )
    mensaje = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(attrs={**WIDGET_CLASS, "rows": 4}),
    )


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
