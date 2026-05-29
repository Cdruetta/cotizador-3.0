from django import forms

from ..models.productos import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "descripcion", "tipo", "precio_unitario",
            "stock", "proveedor", "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProductoFilterForm(forms.Form):
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Buscar producto..."}),
    )
    proveedor = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    activo = forms.ChoiceField(
        required=False,
        choices=[("", "Todos"), ("1", "Activos"), ("0", "Inactivos")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..models.proveedores import Proveedor
        proveedores = Proveedor.objects.all()
        self.fields["proveedor"].choices = [("", "Todos")] + [(p.id, p.nombre) for p in proveedores]


class ProductoImportForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel o CSV",
        help_text="Columnas: nombre (obligatorio), tipo, proveedor, stock, precio, activo.",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".xlsx,.csv"}),
    )
