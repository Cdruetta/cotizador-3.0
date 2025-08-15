#!/bin/bash

# Script de instalación para el Sistema de Cotizaciones Django
echo "🚀 Instalando Sistema de Cotizaciones Django..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3 primero."
    exit 1
fi

echo "✅ Python 3 encontrado"

# Crear directorio del proyecto
PROJECT_DIR="sistema-cotizaciones"
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  El directorio $PROJECT_DIR ya existe. ¿Desea continuar? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Instalación cancelada"
        exit 1
    fi
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs
mkdir -p media
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Ejecutar migraciones
echo "🗄️  Configurando base de datos..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
echo "👤 Creando superusuario..."
echo "Por favor ingresa los datos del administrador:"
python manage.py createsuperuser

# Recopilar archivos estáticos
echo "📋 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo ""
echo "Para iniciar el servidor de desarrollo:"
echo "1. Activa el entorno virtual: source venv/bin/activate"
echo "2. Ejecuta el servidor: python manage.py runserver"
echo "3. Abre tu navegador en: http://127.0.0.1:8000/"
echo ""
echo "Para acceder al panel de administración:"
echo "http://127.0.0.1:8000/admin/"
echo ""
echo "¡Disfruta usando el Sistema de Cotizaciones! 🚀"
