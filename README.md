#
:mybills - Gestor de Gastos e Ingresos

Una aplicación web monolítica desarrollada con FastAPI, Jinja2 y MongoDB para gestionar transacciones financieras personales.

## Características

- Autenticación con sesiones
- Gestión de transacciones (gastos, ingresos, pagos, transferencias)
- Interface web renderizada del lado del servidor (SSR)
- Base de datos MongoDB (local o Atlas)
- Validaciones y seguridad básica

## Instalación

1. **Clonar el repositorio:**

2. **Crear y activar entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
# Crear archivo .env
echo "MONGODB_URI=mongodb://localhost:27017/mybills" > .env
echo "SECRET_KEY=tu_clave_secreta_muy_segura_aqui" >> .env
```

Para MongoDB Atlas, usa una URI como:
```
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/mybills?retryWrites=true&w=majority
```

## Ejecución

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

La aplicación estará disponible en: http://localhost:8000

## Estructura del Proyecto

```
mybills/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuración y variables de entorno
│   ├── database.py        # Conexión a MongoDB
│   ├── models.py          # Modelos de datos (Usuario, Transacción)
│   ├── auth.py            # Autenticación y gestión de sesiones
│   ├── routes.py          # Rutas de la aplicación
│   └── utils.py           # Utilidades varias
├── templates/
│   ├── base.html          # Template base
│   ├── login.html         # Página de login
│   ├── dashboard.html     # Dashboard principal
│   └── add_transaction.html # Formulario nueva transacción
├── static/
│   └── style.css          # Estilos CSS
├── main.py               # Punto de entrada
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Uso

1. **Crear un usuario inicial** (ejecutar en consola Python):
```python
python simple_setup.py
```

2. **Iniciar sesión** con:
   - Username: `admin`
   - Password: `password123`

3. **Agregar transacciones** desde el dashboard

## Tipos de Transacciones

- **Gasto**: Dinero que sale
- **Ingreso**: Dinero que entra  
- **Pago**: Pagos a terceros
- **Transferencia**: Movimientos entre cuentas

## Orígenes de Transacciones

- Efectivo
- Banco
- Tarjeta de crédito
- Tarjeta de débito
- Transferencia bancaria
- Otro

## Variables de Entorno

- `MONGODB_URI`: URI de conexión a MongoDB
- `SECRET_KEY`: Clave secreta para firmar sesiones

## Desarrollo

Para desarrollo, puedes usar el modo debug:
```bash
python main.py --reload
```
