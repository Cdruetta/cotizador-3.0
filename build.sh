#!/usr/bin/env bash
# Instalar dependencias, migraciones y colectar estáticos
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
