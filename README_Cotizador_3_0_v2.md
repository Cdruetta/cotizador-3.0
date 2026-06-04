# 🚀 Cotizador 3.0

🌐 Demo en vivo: https://gcsoft-demo.onrender.com/
User: demo
Pass: demo123

Sistema integral de gestión comercial desarrollado con **Django**, **Django REST Framework**, **Next.js** y **TypeScript**.

Diseñado para servicios técnicos, comercios y pequeñas empresas que necesitan administrar clientes, productos, proveedores, stock, compras, cotizaciones, recibos, remitos y facturación desde una única plataforma.

---

## ✨ Características

### 👥 Gestión Comercial
- Gestión de clientes
- Gestión de proveedores
- Gestión de productos
- Gestión de categorías
- Gestión de marcas
- Gestión de leads

### 💰 Operaciones Comerciales
- Cotizaciones
- Recibos
- Remitos
- Compras
- Facturación
- Generación automática de documentos PDF

### 📦 Inventario
- Control de stock
- Movimientos de stock
- Seguimiento de existencias
- Historial de operaciones

### 📊 Dashboard y Reportes
- Métricas comerciales
- Indicadores de rendimiento
- Estadísticas de negocio
- Reportes generales

### 🔐 Seguridad
- Registro de usuarios
- Inicio de sesión
- Gestión de permisos

### 🔌 API REST
- Endpoints REST
- Serialización de datos con Django REST Framework
- Preparado para integraciones externas

---

## 🛠️ Tecnologías

### Backend
- Python
- Django
- Django REST Framework
- ReportLab

### Frontend
- Next.js 15
- React
- TypeScript
- Tailwind CSS

### Base de Datos
- PostgreSQL (Producción)
- SQLite (Desarrollo)

### DevOps
- GitHub Actions
- Render
- Gunicorn

---

## 🏗️ Arquitectura

Frontend (Next.js)
        ↓
API REST (Django REST Framework)
        ↓
PostgreSQL / SQLite

---

## 📸 Capturas

Coloca aquí tus screenshots desde /docs/screenshots

---

## ⚙️ Instalación Local

### Backend
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

---

## 🚀 Deploy
- Render: https://gcsoft-demo.onrender.com/
- Build: ./build.sh
- Start: gunicorn --chdir backend proyecto.wsgi:application

---

## 🧪 Testing
```bash
python manage.py test
```

---

## 🛣️ Roadmap
- AFIP / ARCA integration
- Facturación electrónica
- Dashboard avanzado
- Exportación Excel
- Multiempresa

---

## 👨‍💻 Autor
Cristian Druetta  
GitHub: https://github.com/Cdruetta

---

## 📄 Licencia
MIT License
