from django import forms
from ..models import ConfiguracionAFIP, Factura, ItemFactura

class ConfiguracionAFIPForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionAFIP
        fields = ['cuit', 'razon_social', 'domicilio', 'punto_venta', 'ambiente', 'certificado', 'clave_privada']
        widgets = {
            'cuit': forms.TextInput(attrs={'placeholder': '20-12345678-9'}),
        }

class GenerarCSRForm(forms.Form):
    cuit         = forms.CharField(max_length=13, label='CUIT', help_text='Formato: 20-12345678-9')
    razon_social = forms.CharField(max_length=255, label='Razón Social')

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'punto_venta']

class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        fields = ['descripcion', 'cantidad', 'precio_unit']