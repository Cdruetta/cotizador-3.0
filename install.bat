@echo off
chcp 65001 >nul
echo.
echo --- Instalando Sistema de Cotizaciones Django ---
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado.
    echo Por favor descarga e instala Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo OK: Python encontrado
python --version

REM Verificar si pip esta disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no esta disponible.
    echo Por favor, verifica tu instalacion de Python.
    pause
    exit /b 1
)

echo OK: pip encontrado

REM Crear entorno virtual
echo.
echo --- Creando entorno virtual ---
python -m venv venv
if errorlevel 1 (
    echo ERROR: Error al crear entorno virtual.
    pause
    exit /b 1
)

REM Activar entorno virtual
echo --- Activando entorno virtual ---
call venv\Scripts\activate.bat

REM Actualizar pip
echo --- Actualizando pip ---
python -m pip install --upgrade pip

REM Instalar dependencias
echo --- Instalando dependencias ---
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Error al instalar dependencias.
    pause
    exit /b 1
)

REM Crear directorios necesarios
echo --- Creando directorios ---
if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images
if not exist "cotizaciones\migrations" mkdir cotizaciones\migrations

REM Crear archivo __init__.py en migrations si no existe
if not exist "cotizaciones\migrations\__init__.py" (
    echo. > cotizaciones\migrations\__init__.py
)

REM Ejecutar migraciones
echo.
echo --- Configurando base de datos (migraciones) ---
python manage.py makemigrations cotizaciones
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Error en migraciones.
    pause
    exit /b 1
)

REM Crear superusuario
echo.
echo --- Creando superusuario ---
echo Por favor ingresa los datos del administrador:
python manage.py createsuperuser

REM Recopilar archivos estaticos
echo.
echo --- Recopilando archivos estaticos ---
python manage.py collectstatic --noinput

echo.
echo --- Instalacion completada exitosamente! ---
echo.
echo ==========================================
echo Para iniciar el servidor de desarrollo:
echo ==========================================
echo 1. Abre una nueva ventana de CMD en esta carpeta.
echo 2. Activa el entorno virtual: venv\Scripts\activate.bat
echo 3. Ejecuta el servidor: python manage.py runserver
echo 4. Abre tu navegador en: http://127.0.0.1:8000/
echo.
echo Para acceder al panel de administracion:
echo http://127.0.0.1:8000/admin/
echo.
echo ==========================================
echo Archivos importantes:
echo ==========================================
echo - Base de datos: db.sqlite3
echo - Configuracion: proyecto\settings.py
echo - Logs: logs\
echo - Media: media\
echo.
echo --- Disfruta usando el Sistema de Cotizaciones! ---
echo.
pause
