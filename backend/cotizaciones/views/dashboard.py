from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..services.analytics.reportes import build_reportes_context
from ..services.dashboard.dashboard_service import build_dashboard_context


@login_required
def dashboard(request):
    context = build_dashboard_context()
    return render(request, "cotizaciones/dashboard.html", context)


@login_required
def reportes(request):
    context = build_reportes_context(request)
    return render(request, "cotizaciones/reportes.html", context)