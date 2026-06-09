# Guía Completa — Cotizador 3.0

Sistema Integral de Gestión Comercial (Django + Next.js)

---

## Índice
1. [Arquitectura](#1-arquitectura)
2. [Setup Local](#2-setup-local)
3. [Modelos / Base de Datos](#3-modelos)
4. [URLs / Rutas](#4-urls)
5. [Vistas](#5-vistas)
6. [Templates](#6-templates)
7. [API REST](#7-api-rest)
8. [Servicios / PDF / AFIP](#8-servicios)
9. [Seguridad](#9-seguridad)
10. [Deploy](#10-deploy)
11. [Comandos Útiles](#11-comandos-útiles)

---

## 1. Arquitectura

```
cotizador-3.0/
├── manage.py              ← Entry point (wrapper → backend/)
├── .env                   ← Variables de entorno (DEBUG, SECRET_KEY)
├── requirements.txt       ← Python dependencies
├── backend/
│   ├── manage.py          ← Django manage.py real
│   ├── proyecto/          ← Config del proyecto Django
│   │   ├── settings.py    ← Config principal (472 líneas)
│   │   ├── urls.py        ← Rutas principales
│   │   ├── urls_api.py    ← Rutas de la API REST
│   │   ├── wsgi.py        ← WSGI para producción
│   │   └── asgi.py        ← ASGI
│   ├── cotizaciones/      ← Única app del proyecto
│   │   ├── models/        ← 17 modelos (split en módulos)
│   │   ├── views/         ← 90+ vistas (split en módulos)
│   │   ├── forms/         ← 18 formularios
│   │   ├── services/      ← Capa de servicios
│   │   ├── templates/     ← 52 templates
│   │   ├── urls.py        ← 80+ rutas
│   │   ├── admin.py       ← Config admin Django
│   │   ├── serializers.py ← DRF serializers
│   │   └── tests/         ← Tests
│   ├── static/            ← CSS, JS, imágenes
│   └── templates/         ← Login, Register, base.html
├── frontend/              ← Next.js 15 (en desarrollo inicial)
│   ├── app/               ← App Router
│   ├── components/ui/     ← 55+ shadcn/ui components
│   └── package.json
└── docs/                  ← Documentación y screenshots
```

---

## 2. Setup Local

### Requisitos
- Python 3.12+
- Node.js 18+ (solo para frontend)

### Backend

```bash
# Clonar y entrar
git clone <repo> && cd cotizador-3.0

# Crear .env
echo 'DEBUG=True' > .env

# Virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Base de datos (SQLite en desarrollo)
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Correr servidor
python manage.py runserver
```

### Frontend (opcional)

```bash
cd frontend
npm install
npm run dev
```

### Variables de entorno (`.env`)

```
DEBUG=True                          # Activa SQLite, desactiva checks de producción
SECRET_KEY=tu-clave-segura          # Django secret key
DATABASE_URL=postgres://...         # Opcional: URL completa de DB
DB_NAME=                            # Opcional: DB name
DB_USER=                            # Opcional: DB user
DB_PASSWORD=                        # Opcional: DB pass
DB_HOST=                            # Opcional: DB host
DB_PORT=5432                        # Opcional: DB port (default 5432)
AXES_ENABLED=True                   # Bloqueo por intentos
AXES_COOLOFF_TIME_MINUTES=15        # Tiempo de bloqueo
AXES_FAILURE_LIMIT=5                # Intentos antes de bloquear
EMAIL_HOST=smtp.gmail.com           # Config email
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SENTRY_DSN=                         # Error monitoring (opcional)
```

---

## 3. Modelos

### 3.1 Cliente
| Campo | Tipo | Detalle |
|-------|------|---------|
| `nombre` | CharField(255) | `db_index=True` |
| `email` | EmailField | nullable |
| `telefono` | CharField(20) | nullable |
| `direccion` | TextField | nullable |
| `localidad` | CharField(100) | nullable |
| `activo` | BooleanField | default=True |
| `created_at` / `updated_at` | DateTimeField | auto |
| `history` | HistoricalRecords | Auditoría |

### 3.2 Producto
| Campo | Tipo | Detalle |
|-------|------|---------|
| `nombre` | CharField(255) | `db_index=True` |
| `descripcion` | TextField | nullable |
| `tipo` | CharField(20) | producto / servicio_soft / servicio_hard |
| `precio_unitario` | DecimalField(10,2) | Min 0 |
| `stock` | PositiveIntegerField | default=0 |
| `proveedor` | ForeignKey(Proveedor) | CASCADE |
| `activo` | BooleanField | default=True |

### 3.3 Cotización
| Campo | Tipo | Detalle |
|-------|------|---------|
| `numero` | CharField(20) | unique, nullable |
| `cliente` | ForeignKey(Cliente) | CASCADE |
| `tipo_documento` | CharField(20) | presupuesto / recibo |
| `fecha` | DateField | auto_now_add |
| `descuento_porcentaje` | DecimalField(5,2) | 0-100 |
| `subtotal_bruto` | DecimalField(12,2) | |
| `monto_descuento` | DecimalField(12,2) | |
| `total` | DecimalField(12,2) | Min 0 |
| `usuario` | ForeignKey(User) | CASCADE |
| `estado` | CharField(20) | borrador / enviada / aprobada / rechazada / facturada |
| `calcular_total()` | Method | Recalcula items + descuento |

### 3.4 CotizaciónItem
| Campo | Tipo | Detalle |
|-------|------|---------|
| `cotizacion` | ForeignKey(Cotizacion) | CASCADE, related_name="items" |
| `producto` | ForeignKey(Producto) | CASCADE |
| `cantidad` | PositiveIntegerField | default=1 |
| `precio_unitario` | DecimalField(10,2) | |
| `subtotal` | DecimalField(12,2) | auto-calculado en save() |

### 3.5 Factura
| Campo | Tipo | Detalle |
|-------|------|---------|
| `cliente` | ForeignKey(Cliente) | PROTECT |
| `tipo` | CharField(1) | 'C' (Monotributo) |
| `punto_venta` | IntegerField | default=1 |
| `numero` | IntegerField | nullable, `db_index=True` |
| `fecha` | DateField | auto_now_add |
| `neto` | DecimalField(12,2) | |
| `total` | DecimalField(12,2) | |
| `cae` | CharField(14) | Código de Autorización Electrónica |
| `cae_vencimiento` | DateField | nullable |
| `estado` | CharField(10) | borrador / autorizada / anulada |

### 3.6 Recibo
| Campo | Tipo | Detalle |
|-------|------|---------|
| `numero` | CharField(50) | unique |
| `cliente` | ForeignKey(Cliente) | CASCADE |
| `fecha` | DateField | |
| `total` | DecimalField(12,2) | |
| `forma_pago` | CharField(20) | efectivo / transferencia / cheque / tarjeta_debito / tarjeta_credito / mercadopago / otro |

### 3.7 Otros modelos

- **Proveedor** — nombre, email, teléfono, dirección, contacto
- **Categoria** — nombre, descripción, activo
- **Marca** — nombre, descripción, activo
- **Lead** — nombre, email, teléfono, empresa, estado (nuevo→contactado→calificado→propuesta→negociacion→ganado/perdido), fuente, asignado_a
- **Compra** — número, proveedor, fecha, total, estado (pendiente/recibida/cancelada)
- **Remito** — número, cliente, fecha, dirección_entrega, estado (pendiente/entregado/cancelado)
- **MovimientoStock** — producto, tipo (entrada/salida/ajuste), cantidad, stock_resultante, motivo
- **ListaPrecio** — nombre, porcentaje (recargo), por_defecto
- **ListaPrecioItem** — lista, categoria, servicio, precio, orden
- **Configuracion** — empresa_nombre, dirección, teléfono, email, ciudad (singleton pk=1)
- **ConfiguracionAFIP** — CUIT, razón social, punto_venta, ambiente, certificados
- **TiendaWebConfig** — activa, nombre_tienda, descripción, email_contacto

---

## 4. URLs

### Rutas principales (`backend/proyecto/urls.py`)

| Path | Destino |
|------|---------|
| `/admin/` | Django Admin |
| `/api/` | API REST (DRF) |
| `/` | App principal (cotizaciones) |
| `/swagger/` | Documentación Swagger |
| `/redoc/` | Documentación ReDoc |

### API REST (`/api/`)

| Path | Métodos | Descripción |
|------|---------|-------------|
| `auth/token/` | POST | Obtener JWT (user/pass) |
| `auth/token/refresh/` | POST | Refrescar JWT |
| `v3/clientes/` | GET/POST | CRUD clientes |
| `v3/productos/` | GET/POST | CRUD productos |
| `v3/cotizaciones/` | GET/POST | CRUD cotizaciones |
| `v3/detalles-cotizacion/` | GET/POST | CRUD items cotización |
| `v3/facturas/` | GET/POST | CRUD facturas |

### App (`/cotizaciones/urls.py` — 80+ rutas)

**Módulos principales:**

| Prefix | Funcionalidad |
|--------|---------------|
| `/` | Dashboard |
| `/login/`, `/logout/`, `/register/` | Auth |
| `/usuarios/` | CRUD usuarios |
| `/clientes/` | CRUD + import/export Excel/PDF |
| `/proveedores/` | CRUD |
| `/productos/` | CRUD |
| `/cotizaciones/` | CRUD + PDF + email + cambio estado |
| `/facturacion/` | CRUD + autorizar AFIP + PDF + config |
| `/recibos/` | CRUD + PDF + email |
| `/remitos/` | CRUD |
| `/comprobantes/` | Listado general |
| `/leads/` | CRUD |
| `/compras/` | CRUD |
| `/categorias/` | CRUD |
| `/marcas/` | CRUD |
| `/stock/` | Listado + export/import Excel/PDF |
| `/stock/movimientos/` | CRUD movimientos |
| `/listas-precio/` | CRUD + CSV import + PDF + aplicar precios |
| `/roles/` | CRUD grupos/permisos |
| `/reportes/` | Reportes |
| `/configuracion/` | Config general |
| `/tienda-web/` | Config tienda online |

---

## 5. Vistas

Organizadas en `backend/cotizaciones/views/`:

| Archivo | Vistas principales |
|---------|-------------------|
| `dashboard.py` | `dashboard()`, `reportes()` |
| `auth.py` | `register()` |
| `users.py` | `UserListView`, `UserCreateView` |
| `clientes.py` | `ClienteListView/CreateView/UpdateView/DeleteView/DetailView`, toggle, import/export |
| `proveedores.py` | CRUD completo |
| `productos.py` | CRUD completo |
| `cotizaciones.py` | CRUD + `cambiar_estado`, `agregar/eliminar_item`, `generar_pdf`, `enviar_email`, `actualizar_descuento` |
| `facturacion.py` | CRUD facturas + `autorizar`, `agregar_item`, `generar_pdf`, `config_afip`, `generar_csr`, `test_conexion`, `crear_desde_cotizacion` |
| `recibos.py` | CRUD + `agregar/eliminar_item`, `generar_pdf`, `enviar_email` |
| `comprobantes.py` | `ComprobanteListView` |
| `leads.py` | CRUD |
| `compras.py` | CRUD + `agregar/eliminar_item` |
| `remitos.py` | CRUD |
| `categorias.py` | CRUD |
| `marcas.py` | CRUD |
| `movimientos_stock.py` | List + Create |
| `stock.py` | List + export/import |
| `listas_precio.py` | CRUD + items + CSV import + PDF + aplicar precios |
| `roles.py` | CRUD grupos |
| `config.py` | `configuracion()` |
| `tienda_web.py` | `tienda_web_config()` |
| `reportes.py` | `reportes_view()` |
| `api.py` | ViewSets (Cliente, Producto, Cotizacion, CotizacionItem, Factura) + endpoints auxiliares |

---

## 6. Templates

52 templates Django en `backend/templates/`:

| Carpeta | Templates |
|---------|-----------|
| Raíz | `base.html` (layout principal con sidebar + topbar) |
| `registration/` | `login.html` (522 líneas, diseño animado), `register.html` |
| `axes/` | `lockout.html` (pantalla de bloqueo) |
| `cotizaciones/` | dashboard, reportes, config, user_list/form |
| `cotizaciones/cliente/` | list, form, detail, confirm_delete |
| `cotizaciones/producto/` | list, form, detail, confirm_delete |
| `cotizaciones/cotizacion/` | list, form, detail, confirm_delete |
| `cotizaciones/proveedor/` | list, form, detail, confirm_delete |
| `cotizaciones/facturacion/` | factura_list, factura_form, factura_detail, config_afip |
| `cotizaciones/recibo/` | list, form, detail |
| `cotizaciones/compra/` | list, form, detail |
| `cotizaciones/remito/` | list, form |
| `cotizaciones/lead/` | list, form |
| `cotizaciones/stock/` | list |
| `cotizaciones/movimiento_stock/` | list, form |
| `cotizaciones/categoria/` | list, form |
| `cotizaciones/marca/` | list, form |
| `cotizaciones/listaprecio/` | list, form, detail |
| `cotizaciones/comprobante/` | list |
| `cotizaciones/roles/` | list, form |
| `cotizaciones/tiendaweb/` | config |

**base.html** — El layout principal incluye:
- Sidebar colapsable con búsqueda de menú (filtrado JS)
- Topbar con dólar (API), clima, fecha, notificaciones, selector de tema
- Sistema de mensajes tipo toast (sonner)
- Tema oscuro/claro con persistencia localStorage
- Responsive: sidebar con backdrop en mobile

---

## 7. API REST

### Endpoints

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/auth/token/` | POST | No | Login JWT |
| `/api/auth/token/refresh/` | POST | No | Refresh JWT |
| `/api/v3/clientes/` | GET/POST | JWT | Listar/Crear clientes |
| `/api/v3/clientes/{id}/` | GET/PUT/PATCH/DELETE | JWT | CRUD cliente |
| `/api/v3/productos/` | GET/POST | JWT | Listar/Crear productos |
| `/api/v3/productos/{id}/` | GET/PUT/PATCH/DELETE | JWT | CRUD producto |
| `/api/v3/cotizaciones/` | GET/POST | JWT | Listar/Crear cotizaciones |
| `/api/v3/cotizaciones/{id}/` | GET/PUT/PATCH/DELETE | JWT | CRUD cotización |
| `/api/v3/detalles-cotizacion/` | GET/POST | JWT | Items de cotización |
| `/api/v3/facturas/` | GET/POST | JWT | Listar/Crear facturas |
| `/api/v3/facturas/{id}/` | GET/PUT/PATCH/DELETE | JWT | CRUD factura |

### Filtros disponibles (vía query params)
- `clientes`: `search`, `activo`
- `productos`: `search`, `tipo`, `activo`, `proveedor_id`
- `cotizaciones`: `search`, `estado`, `cliente_id`, `fecha_desde`, `fecha_hasta`
- `facturas`: `search`, `estado`, `cliente_id`

### Autenticación
- JWT (access token 60min, refresh token 1 día)
- Header: `Authorization: Bearer <token>`
- Refresh: POST a `/api/auth/token/refresh/` con `{"refresh": "<token>"}`

---

## 8. Servicios

### PDF (`services/documents/pdf.py`)
- Genera PDFs profesionales para Cotizaciones y Facturas
- Incluye logo, QR (AFIP para facturas), tablas estilizadas, pie de página
- Usa ReportLab

### AFIP/ARCA (`services/arca/`)
- `afip_stub.py` — Stub para pruebas sin conexión real
- `conexion.py` — Conexión WSAA + generación de tickets de acceso
- `csr.py` — Generación de Certificate Signing Request
- Integración con Factura C (Monotributo)

### Import/Export
- **Clientes**: importación Excel (openpyxl), exportación Excel y PDF
- **Productos**: importación Excel, exportación Excel y PDF
- **Stock**: exportación Excel y PDF, importación Excel
- **Listas de precio**: importación CSV, exportación PDF

### Dashboard
- `dashboard_service.py` — Métricas: ventas hoy, cotizaciones pendientes, productos bajos stock, total clientes

### Email
- `communication/email.py` — Envío de cotizaciones y recibos por email vía SMTP

---

## 9. Seguridad

### Django Axes (protección fuerza bruta)
- 5 intentos fallidos → bloqueo 15 minutos
- Bloqueo por usuario (no por IP)
- Mensajes personalizados en español

### Content Security Policy (CSP)
- Restringe orígenes de scripts, estilos, fuentes
- Permite CDNs específicas (Bootstrap, jsdelivr, dolarapi)

### Producción
- Cookies seguras (Secure, HttpOnly, SameSite=Lax)
- HSTS (1 año, subdominios, preload)
- SSL redirect forzado
- XSS filter, nosniff

### API
- JWT con expiración
- Throttling: 20 req/min anónimo, 200 req/min autenticado
- CORS configurado

---

## 10. Deploy

### Render (`render.yaml`)
- Servicio web: `gunicorn --chdir backend proyecto.wsgi:application`
- Python 3.13.4
- Build: `./build.sh` (pip install → migrate → collectstatic)
- PostgreSQL como base de datos

### Variables de entorno requeridas en producción
```
DEBUG=False
SECRET_KEY=<obligatorio>
DATABASE_URL=postgres://<url>
ALLOWED_HOSTS=<dominio>
CSRF_TRUSTED_ORIGINS=https://<dominio>
```

---

## 11. Comandos Útiles

```bash
# Development
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # Accesible desde la red

# Base de datos
python manage.py migrate              # Aplicar migraciones
python manage.py makemigrations       # Crear migraciones
python manage.py showmigrations       # Ver estado
python manage.py sqlmigrate <app> <#> # Ver SQL

# Usuarios
python manage.py createsuperuser
python manage.py changepassword <user>

# Tests
python manage.py test
python manage.py test cotizaciones.tests.test_models
python manage.py test cotizaciones.tests.test_views

# Shell
python manage.py shell
python manage.py shell_plus  # Si django-extensions está instalado

# Colección de estáticos
python manage.py collectstatic

# Management commands propios
python manage.py productos_cargar  # Carga datos iniciales
python manage.py productos_aumentar_precios  # Aumento masivo

# Frontend (Next.js)
cd frontend && npm run dev
cd frontend && npm run build
cd frontend && npm run lint
```

---

## Estructura de archivos clave

```
backend/
├── proyecto/settings.py        ← Configuración general (DB, auth, seguridad, etc.)
├── proyecto/urls.py            ← Rutas raíz
├── proyecto/urls_api.py        ← Rutas API REST
├── cotizaciones/urls.py        ← 80+ rutas de la app
├── cotizaciones/models/        ← 17 modelos en módulos separados
├── cotizaciones/views/         ← 90+ vistas en módulos separados
├── cotizaciones/forms/         ← 18 formularios
├── cotizaciones/services/      ← Lógica de negocio (PDF, AFIP, import/export)
├── cotizaciones/admin.py       ← Config panel admin Django
├── cotizaciones/serializers.py ← Serializers DRF
├── cotizaciones/tests/         ← Tests unitarios
├── templates/base.html         ← Layout principal (responsive, sidebar, tema)
├── static/js/main.js           ← JavaScript global
└── static/styles/globales.css  ← Estilos globales + responsive
```
