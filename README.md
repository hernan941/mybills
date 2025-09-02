# 💰 MyBills - Gestor de Gastos e Ingresos

Una aplicación web moderna para gestionar tus finanzas personales, desarrollada con FastAPI, Jinja2 y MongoDB.

## ✨ Características

- 🔐 **Autenticación segura** con sesiones
- 💸 **Gestión completa de transacciones** (gastos, ingresos, pagos, transferencias)
- 🎨 **Interface web responsiva** renderizada del lado del servidor (SSR)
- 🗄️ **Base de datos MongoDB** (local o Atlas)
- 🛡️ **Validaciones y seguridad** integradas
- 📊 **Dashboard intuitivo** para visualizar tus finanzas

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- MongoDB (local) o cuenta de MongoDB Atlas
- Git

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <tu-repositorio>
   cd webmybills
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o en Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus configuraciones
   ```

   **Ejemplo de .env:**
   ```env
   MONGODB_URI=mongodb://localhost:27017/mybills
   SECRET_KEY=tu_clave_secreta_super_segura_de_al_menos_32_caracteres
   DEBUG=True
   ```

   **Para MongoDB Atlas:**
   ```env
   MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/mybills?retryWrites=true&w=majority
   ```

5. **Ejecutar la aplicación:**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Acceder a la aplicación:**
   
   Abre tu navegador en: http://localhost:8000

## 📁 Estructura del Proyecto

```
webmybills/
├── 📁 app/
│   ├── __init__.py
│   ├── config.py          # ⚙️ Configuración y variables de entorno
│   ├── database.py        # 🗄️ Conexión a MongoDB
│   ├── models.py          # 📋 Modelos de datos (Usuario, Transacción)
│   ├── auth.py            # 🔐 Autenticación y gestión de sesiones
│   ├── routes.py          # 🛤️ Rutas de la aplicación
│   └── utils.py           # 🔧 Utilidades varias
├── 📁 templates/
│   ├── base.html          # 🎨 Template base
│   ├── login.html         # 🔑 Página de login
│   ├── dashboard.html     # 📊 Dashboard principal
│   └── add_transaction.html # ➕ Formulario nueva transacción
├── 📁 static/
│   └── style.css          # 🎨 Estilos CSS
├── main.py               # 🚀 Punto de entrada
├── requirements.txt      # 📦 Dependencias
├── simple_setup.py       # ⚡ Script de configuración inicial
└── README.md            # 📖 Esta documentación
```

## 👤 Configuración Inicial

1. **Crear usuario administrador:**
   ```bash
   python simple_setup.py
   ```

2. **Credenciales por defecto:**
   - **Usuario:** `admin`
   - **Contraseña:** `password123`

   > ⚠️ **Importante:** Cambia estas credenciales en producción

## 💡 Uso de la Aplicación

### Tipos de Transacciones

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| 💸 **Gasto** | Dinero que sale de tu bolsillo | Compra de comida, gasolina |
| 💰 **Ingreso** | Dinero que recibes | Salario, freelance |
| 💳 **Pago** | Pagos a terceros o servicios | Facturas, préstamos |
| 🔄 **Transferencia** | Movimientos entre cuentas | Ahorro a cuenta corriente |

### Orígenes de Transacciones

- 💵 Efectivo
- 🏦 Banco
- 💳 Tarjeta de crédito
- 💰 Tarjeta de débito
- 📱 Transferencia bancaria
- ❓ Otro

## ⚙️ Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `MONGODB_URI` | URI de conexión a MongoDB | `mongodb://localhost:27017/mybills` |
| `SECRET_KEY` | Clave secreta para sesiones | `mi-clave-super-secreta-123` |
| `DEBUG` | Modo desarrollo (opcional) | `True` o `False` |

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Comandos útiles:
```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests (si están configurados)
pytest

# Formatear código
black app/

# Linting
flake8 app/
```

## 🐳 Docker (Opcional)

Si prefieres usar Docker:

```bash
# Construir imagen
docker build -t mybills .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env mybills
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa los [Issues existentes](../../issues)
2. Crea un [nuevo Issue](../../issues/new)
3. Consulta la documentación de [FastAPI](https://fastapi.tiangolo.com/)

---

**¡Hecho con ❤️ para ayudarte a