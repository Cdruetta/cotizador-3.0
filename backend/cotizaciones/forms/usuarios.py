from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .common import WIDGET_CLASS


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

