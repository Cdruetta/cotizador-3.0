#!/usr/bin/env bash
#!/bin/bash

# Actualizar pip, setuptools y wheel
pip install --upgrade pip setuptools wheel

# Instalar dependencias desde la ruta correcta
pip install -r ../scripts/requirements.txt

# Migraciones
python manage.py migrate --noinput

# Archivos estáticos
python manage.py collectstatic --noinput
