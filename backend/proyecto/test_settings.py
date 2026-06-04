# proyecto/test_settings.py

# 1. Importas toda tu configuración actual
from .settings import *

# 2. Sobrescribes solo el motor de archivos estáticos
# Esto le dice a Django: "Para las pruebas, usa el almacenamiento normal, no busques manifiestos"
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'