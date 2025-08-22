#!/usr/bin/env bash
set -e

echo "🔹 Actualizando pip, setuptools y wheel..."
pip install --upgrade pip setuptools wheel

echo "🔹 Instalando dependencias..."
pip install -r requirements.txt

echo "🔹 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🔹 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Build completado"
