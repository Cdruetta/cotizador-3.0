from django import forms
from .models.cotizaciones import Cotizacion, CotizacionItem

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['cliente', 'vencimiento', 'estado']
        widgets = {'vencimiento': forms.DateInput(attrs={'type': 'date'})}

class CotizacionItemForm(forms.ModelForm):
    class Meta:
        model = CotizacionItem
        fields = ['producto', 'cantidad', 'precio_unitario', 'nota']

class CotizacionFilterForm(forms.Form):
    search = forms.CharField(required=False, label="Buscar")
    estado = forms.ChoiceField(choices=[('', 'Todos')] + Cotizacion.ESTADO_CHOICES, required=False)

class EnviarEmailForm(forms.Form):
    email_destino = forms.EmailField()
    asunto = forms.CharField(max_length=200)
    mensaje = forms.CharField(widget=forms.Textarea)