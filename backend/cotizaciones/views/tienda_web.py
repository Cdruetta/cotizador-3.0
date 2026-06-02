from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models.tienda_web import TiendaWebConfig
from ..forms.tienda_web import TiendaWebConfigForm


@login_required
def tienda_web_config(request):
    if not request.user.is_staff:
        messages.error(request, "No tenés permiso para acceder a esta página.")
        return redirect("dashboard")

    config, _ = TiendaWebConfig.objects.get_or_create(pk=1)

    if request.method == "POST":
        form = TiendaWebConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración de tienda web guardada exitosamente.")
            return redirect("tienda_web_config")
    else:
        form = TiendaWebConfigForm(instance=config)

    return render(request, "cotizaciones/tiendaweb/config.html", {"form": form, "config": config})
