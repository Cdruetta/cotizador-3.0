from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User

from apps.core.models import Configuracion

WIDGET_CLASS = {"class": "form-control"}
SELECT_CLASS = {"class": "form-select"}


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            "ciudad_nombre",
            "latitud",
            "longitud",
            "empresa_nombre",
            "empresa_direccion",
            "empresa_telefono",
            "empresa_email",
        ]
        widgets = {
            "ciudad_nombre": forms.TextInput(attrs={**WIDGET_CLASS, "placeholder": "Ej: Río Cuarto"}),
            "latitud": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.000001"}),
            "longitud": forms.NumberInput(attrs={**WIDGET_CLASS, "step": "0.000001"}),
            "empresa_nombre": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_direccion": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_telefono": forms.TextInput(attrs=WIDGET_CLASS),
            "empresa_email": forms.EmailInput(attrs=WIDGET_CLASS),
        }


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos",
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Vendedores"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "permissions":
                continue
            css = field.widget.attrs.get("class", "")
            if "form-control" not in css and "form-select" not in css:
                field.widget.attrs["class"] = "form-control"


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=WIDGET_CLASS))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=WIDGET_CLASS))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=WIDGET_CLASS))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {"username": forms.TextInput(attrs=WIDGET_CLASS)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(WIDGET_CLASS)
        self.fields["password2"].widget.attrs.update(WIDGET_CLASS)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
