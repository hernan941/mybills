# 💰 MyBills - Gestor de Gastos e Ingresos

Una aplicación web moderna para gestionar tus finanzas personales, desarrollada con FastAPI, Jinja2 y MongoDB.

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

## 👤 Configuración Inicial

1. **Crear usuario administrador:**
   ```bash
   python simple_setup.py
   ```

2. **Credenciales por defecto:**
   - **Usuario:** `admin`
   - **Contraseña:** `password123`

   > ⚠️ **Importante:** Cambia estas credenciales en producción

## 🤖 Integración Automática con Google Apps Script

MyBills incluye un sistema de webhook que permite recibir automáticamente emails de comprobantes de Tenpo y convertirlos en transacciones.

### Configuración de Google Apps Script

1. **Crear un nuevo proyecto en Google Apps Script:**
   - Ve a [script.google.com](https://script.google.com)
   - Crea un nuevo proyecto

2. **Añadir el código del script:**
   ```javascript
   function forwardToWebhook() {
     var threads = GmailApp.search('from:no-reply@tenpo.cl is:unread');
     
     for (var i = 0; i < threads.length; i++) {
       var messages = threads[i].getMessages();
       
       for (var j = 0; j < messages.length; j++) {
         var msg = messages[j];
         
         var payload = "subject=" + encodeURIComponent(msg.getSubject()) + 
                       "&body=" + encodeURIComponent(msg.getPlainBody());
         
         console.log(payload);
         
         UrlFetchApp.fetch("https://tu-dominio.com/webhook/email", {
           method: "post",
           contentType: "application/x-www-form-urlencoded",
           payload: payload  
         });
         
         msg.markRead(); // Marca solo el mensaje leído, no todo el thread
       }
     }
   }
   ```

3. **Configurar el webhook:**
   - Reemplaza `https://tu-dominio.com/webhook/email` con la URL real de tu aplicación
   - El script busca emails no leídos de `no-reply@tenpo.cl`
   - Envía el asunto y cuerpo del email al webhook de MyBills

4. **Configurar trigger automático:**
   - En Google Apps Script, ve a "Activadores" (Triggers)
   - Crear nuevo activador:
     - Función: `forwardToWebhook`
     - Tipo: Basado en tiempo
     - Frecuencia: Cada 5-15 minutos (según preferencia)

### Cómo Funciona

1. **Recepción de Email**: Cuando recibes un comprobante de Tenpo en tu Gmail
2. **Procesamiento**: Google Apps Script detecta el email y lo envía al webhook
3. **Parsing**: MyBills analiza el contenido y extrae:
   - Monto de la transacción
   - Comercio/descripción
   - Fecha y hora
   - Categoría automática (basada en el nombre del comercio)
4. **Creación**: Se crea automáticamente una nueva transacción en tu dashboard

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. 

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa los [Issues existentes](../../issues)
2. Crea un [nuevo Issue](../../issues/new)
3. Consulta la documentación de [FastAPI](https://fastapi.tiangolo.com/)

