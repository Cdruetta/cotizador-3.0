#!/usr/bin/env bash

# 🛠 Actualiza pip, setuptools y wheel
pip install --upgrade pip setuptools wheel

# 📦 Instala las dependencias
pip install -r requirements.txt

# 🗄 Ejecuta migraciones en la base de datos configurada (PostgreSQL en Render)
python manage.py migrate --noinput

# 🌐 Recolecta archivos estáticos
python manage.py collectstatic --clear --noinput


echo "✅ Build completado"
