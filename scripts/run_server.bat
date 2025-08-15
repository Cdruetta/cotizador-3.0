@echo off
chcp 65001 >nul
echo 🚀 Iniciando Sistema de Cotizaciones Django...
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo Por favor ejecuta install.bat primero
    pause
    exit /b 1
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si la base de datos existe
if not exist "db.sqlite3" (
    echo 🗄️  Configurando base de datos...
    python manage.py makemigrations cotizaciones
    python manage.py migrate
)

REM Iniciar servidor
echo.
echo 🌐 Iniciando servidor de desarrollo...
echo.
echo ==========================================
echo Servidor disponible en:
echo http://127.0.0.1:8000/
echo.
echo Panel de administración:
echo http://127.0.0.1:8000/admin/
echo.
echo Presiona Ctrl+C para detener el servidor
echo ==========================================
echo.

python manage.py runserver
pause
