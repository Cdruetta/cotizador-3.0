from django.urls import path
from apps.core import views

urlpatterns = [
    path('register/', views.register, name='register'),
    # Agregar rutas adicionales para views de core
]