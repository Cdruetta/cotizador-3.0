from django.apps import AppConfig


class CotizacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cotizaciones'
    verbose_name = 'Cotizaciones'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.models_module = None
