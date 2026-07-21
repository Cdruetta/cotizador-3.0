from django import forms

from .models import Categoria, ListaPrecio, Marca, Producto, Proveedor
from apps.core.forms import WIDGET_CLASS


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "direccion", "telefono", "email", "contacto"]
        widgets = {
            "nombre": forms.TextInput(attrs={**WIDGET_CLASS, "required": True}),
            "direccion": forms.TextInput(attrs=WIDGET_CLASS),
            "telefono": forms.TextInput(attrs=WIDGET_CLASS),
            "email": forms.EmailInput(attrs=WIDGET_CLASS),
            "contacto": forms.TextInput(attrs=WIDGET_CLASS),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Insumos de limpieza"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "activo":
                continue
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "activo":
                continue
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"


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
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Precio máx.", "step": "0.01"}),
    )
    tipo = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + Producto.TIPO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proveedores = Proveedor.objects.all()
        self.fields["proveedor"].choices = [("", "Todos")] + [(p.id, p.nombre) for p in proveedores]


class ProductoImportForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel o CSV",
        help_text="Columnas: nombre (obligatorio), tipo, proveedor, stock, precio, activo.",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".xlsx,.csv"}),
    )


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
