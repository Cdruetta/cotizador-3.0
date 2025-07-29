@echo off
chcp 65001 >nul
echo 📊 Creando datos de prueba...
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar script de datos de prueba
python manage.py shell < create_sample_data.py

echo.
echo ✅ Datos de prueba creados exitosamente
echo.
echo Datos creados:
echo - 5 Clientes de ejemplo
echo - 3 Proveedores de ejemplo  
echo - 10 Productos de ejemplo
echo - 3 Cotizaciones de ejemplo
echo.
pause
