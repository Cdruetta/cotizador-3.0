# Estructura del proyecto

## Raiz

- `backend/`: proyecto Django completo.
- `frontend/`: proyecto Next.js completo.
- `manage.py`: wrapper para correr Django desde raiz.
- `Procfile`, `build.sh`, `runtime.txt`: despliegue backend.
- `docs/`: documentacion y notas.

## App `cotizaciones`

- Ruta: `backend/cotizaciones/`
- `views/`: vistas por dominio.
- `forms/`: formularios por dominio.
- `models/`: modelos por dominio.
- `services/`: logica de negocio separada por areas (`analytics`, `communication`, `documents`, `system`).
- `config/`: infraestructura de la app (context processors y settings auxiliares).
- `tests/`: tests de la app.
- `utils/`: utilidades compartidas.
- `management/commands/`: comandos Django custom.

## Convenciones

- Evitar guardar archivos compilados (`__pycache__`, `*.pyc`) en git.
- Mantener imports hacia paquetes (`cotizaciones.views`, `cotizaciones.forms`, etc.).
- Crear nuevos modulos por dominio, no agrandar archivos centrales.
- Ejecutar backend desde raiz con `python manage.py ...`.
- Ejecutar frontend con `npm --prefix frontend run dev`.

