## 1) Ajuste “Nuevo Producto / Nuevo Servicio” (menú)
- [ ] (Opcional según alcance final) Asegurar que el formulario de Producto preseleccione `tipo` si llega por querystring.

## 2) Facturación: items con desplegable de productos/servicios y precio unitario automático
- [ ] Editar `backend/cotizaciones/models/facturacion.py`: agregar FK `producto` en `ItemFactura`.
- [ ] Editar `backend/cotizaciones/models/facturacion.py`: ajustar lógica para que `descripcion` y `precio_unit` se llenen desde el producto.
- [ ] Editar `backend/cotizaciones/forms/facturacion.py`: cambiar `ItemFacturaForm` para usar `producto` (select) y no `descripcion` editable.
- [ ] Editar `backend/cotizaciones/templates/cotizaciones/facturacion/factura_detail.html`: usar formulario con `producto/cantidad/precio_unit` e igual JS que cotización.

## 3) Facturación: crear factura seleccionando cotización (1 cotización → 1 factura)
- [ ] Editar `backend/cotizaciones/models/facturacion.py`: agregar `Factura.cotizacion` como `OneToOneField`.
- [ ] Editar `backend/cotizaciones/forms/facturacion.py`: agregar campo `cotizacion` al `FacturaForm` con filtrado.
- [ ] Editar `backend/cotizaciones/views/facturacion.py`: en `FacturaCreateView.form_valid`, copiar items de la cotización a `ItemFactura` y recalcular totales.
- [ ] Editar `backend/cotizaciones/templates/cotizaciones/facturacion/factura_detail.html`: ocultar “Agregar ítem” si `factura.cotizacion` existe (regla A).
- [ ] Editar `backend/cotizaciones/templates/cotizaciones/facturacion/factura_form.html`: mostrar el selector de cotización.

## 4) Migraciones + validación
- [ ] Correr `python manage.py makemigrations backend`
- [ ] Correr `python manage.py migrate`
- [ ] Probar flujo: crear cotización con productos/servicios → crear factura desde esa cotización → confirmar items y total.

