# Separar Productos en Sidebar - Repuestos vs Servicios

✅ Plan aprobado

**Información Reunida:**
- Model productos.py: tipo = ('producto', 'servicio_soft', 'servicio_hard')
- View productos.py: ProductoListView filtra ?tipo=valor
- Template producto/list.html: filtro tipo + columna tipo
- Sidebar base.html: 1 link productos

**Plan:**
1. ✅ Crear TODO
2. 🔄 views/productos.py: Soporte ?tipo_multiple=soft,hard → Q(tipo__in=...)
3. 🔄 urls.py: urls producto_list_repuestos/producto_list_servicios
4. 🔄 base.html: Reemplazar 1 link → 2 links (Repuestos ?tipo=producto, Servicios ?tipo_multiple=...)
5. 🔄 producto/list.html: Activar filtro múltiples tipos
6. Test: python manage.py runserver + DevTools

**Dependientes:** views/productos.py, urls.py, base.html, templates/producto/list.html

✅ views/productos.py: + soporte tipo_multiple
✅ base.html: Sidebar Repuestos/Servicios links

**Próximo:** Testear + Completar


