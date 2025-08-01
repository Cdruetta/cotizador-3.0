#!/usr/bin/env bash

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
