from django import forms

from ..models import Cotizacion, CotizacionItem, Producto
from .common import WIDGET_CLASS, SELECT_CLASS


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ["cliente", "tipo_documento", "observaciones"]
        widgets = {
            "cliente": forms.Select(attrs=SELECT_CLASS),
            "tipo_documento": forms.Select(attrs=SELECT_CLASS),
            "observaciones": forms.Textarea(attrs={**WIDGET_CLASS, "rows": 3}),
        }

    def _clean_extra_fields(self):
        ignored = {"items", "descuento_pct"}
        for key in ignored:
            self.data._mutable = True
            self.data.pop(key, None)
            self.data._mutable = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data:
            self._clean_extra_fields()


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
        choices=[("", "Todos los tipos")] + Cotizacion.TIPO_DOCUMENTO_CHOICES,
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

