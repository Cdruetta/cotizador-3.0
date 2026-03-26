from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..forms import ConfiguracionForm
from ..models import Configuracion


@login_required
def configuracion(request):
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso para acceder a esta página.")
        return redirect("dashboard")

    config = Configuracion.get()

    if request.method == "POST":
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada exitosamente.")
            return redirect("configuracion")
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, "cotizaciones/configuracion.html", {"form": form, "config": config})

