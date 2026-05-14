# TODO - Optimización rendimiento

## Paso 1: Diagnóstico del dashboard
- [x] Revisar `build_dashboard_context()` y detectar queries repetitivas y potencial falta de índices.

## Paso 2: Implementar mejoras de performance
- [ ] Agregar caché del contexto en `backend/cotizaciones/services/dashboard/dashboard_service.py` (TTL 60-120s).
- [ ] Agregar índices en modelos para campos usados por el dashboard:
  - [ ] `Cotizacion` (fecha/estado) en `backend/cotizaciones/models/cotizaciones.py`
  - [ ] `Factura` (fecha/estado/creada) en `backend/cotizaciones/models/facturacion.py`

## Paso 3: Migraciones y verificación
- [ ] Correr `makemigrations` y `migrate`
- [ ] Probar `/dashboard` y verificar reducción de tiempo

## Paso 4: Validación extra (si sigue lento)
- [ ] Revisar logs de queries / EXPLAIN en DB
- [ ] Ajustar queries y/o agregar paginación/limit adicional en listados

