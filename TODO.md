# TODO

## Cotizaciones: ver detalle y marcar completada
- [x] Ajustar `backend/templates/cotizaciones/cotizacion/detail.html` para que el botón “Marcar completada” use la ruta existente `cambiar_estado_cotizacion`.
- [x] Ajustar `backend/templates/cotizaciones/cotizacion/detail.html` para que use `cotizacion.estado` (no `cotizacion.completada`).
- [x] Definir mapping UI -> estado:
  - [x] “Marcar completada” => `estado='aprobada'`
  - [x] “Reabrir” => `estado='borrador'`
- [ ] (Si es necesario) Validar que `estado` y etiquetas CSS/estados del sistema coincidan en el detalle.
- [ ] Ejecutar tests/sanity check manuales (abrir cotización, marcar completada, verificar estado y acciones relacionadas).

