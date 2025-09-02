from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from bson import ObjectId
import logging

from typing import Optional

from app.config import settings, TRANSACTION_TYPES, TRANSACTION_ORIGINS, COMMON_CATEGORIES
from app.database import get_database, verify_collection_connection
from app.models import Transaction, TransactionSummary, User
from app.auth import auth_manager, get_current_user
from app.utils import (
    format_currency, format_datetime, format_date, humanize_origin,
    humanize_category, humanize_transaction_type, get_transaction_type_color,
    get_transaction_type_icon, validate_metadata_json, paginate_list,
    get_current_month_name
)


from app.parsers import TenpoEmailParser

logger = logging.getLogger(__name__)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Añadir funciones helper a los templates
templates.env.globals["format_currency"] = format_currency
templates.env.globals["format_datetime"] = format_datetime
templates.env.globals["format_date"] = format_date
templates.env.globals["humanize_origin"] = humanize_origin
templates.env.globals["humanize_category"] = humanize_category
templates.env.globals["humanize_transaction_type"] = humanize_transaction_type
templates.env.globals["get_transaction_type_color"] = get_transaction_type_color
templates.env.globals["get_transaction_type_icon"] = get_transaction_type_icon
templates.env.globals["get_current_month_name"] = get_current_month_name

async def get_current_user_from_session(request: Request) -> Optional[User]:
    """Obtiene el usuario actual desde la sesión"""
    session_token = request.cookies.get("session_token")
    if session_token:
        return get_current_user(session_token)
    return None

async def require_auth(request: Request) -> User:
    """Requiere que el usuario esté autenticado"""
    user = await get_current_user_from_session(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    return user

def prepare_chart_data(transactions_list):
    """Prepara los datos para los gráficos de categorías"""
    from app.utils import humanize_category
    
    # Solo procesar gastos para el gráfico de categorías
    gastos = [t for t in transactions_list if t.get('type') == 'gasto']
    
    # Agrupar por categoría
    category_totals = {}
    for transaction in gastos:
        category = transaction.get('category', 'sin_categoria')
        amount = float(transaction.get('amount', 0))
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    # Colores predefinidos para cada categoría
    category_colors = {
        'alimentacion': '#FF6384',
        'transporte': '#36A2EB', 
        'entretenimiento': '#FFCE56',
        'salud': '#4BC0C0',
        'educacion': '#9966FF',
        'hogar': '#FF9F40',
        'trabajo': '#FF6384',
        'compras': '#C9CBCF',
        'servicios': '#4BC0C0',
        'supermercado': '#36A2EB',
        'restaurantes': '#FFCE56',
        'ropa': '#9966FF',
        'otros': '#C9CBCF',
        'sin_categoria': '#E7E9ED'
    }
    
    # Preparar datos para Chart.js
    categories = []
    colors = []
    amounts = []
    
    for category, total in category_totals.items():
        categories.append(humanize_category(category))
        colors.append(category_colors.get(category, '#C9CBCF'))
        amounts.append(total)
    
    return {
        'categories': categories,
        'colors': colors, 
        'amounts': amounts
    }

def create_routes(app: FastAPI):
    """Crea todas las rutas de la aplicación"""
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Página de inicio - redirige al dashboard si está autenticado, sino al login"""
        user = await get_current_user_from_session(request)
        if user:
            return RedirectResponse(url="/dashboard", status_code=302)
        return RedirectResponse(url="/login", status_code=302)

    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        """Página de login"""
        user = await get_current_user_from_session(request)
        if user:
            return RedirectResponse(url="/dashboard", status_code=302)


        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": None
        })

    @app.post("/login", response_class=HTMLResponse)
    async def login_post(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
    ):
        """Procesar login"""
        # Autenticar usuario
        user = auth_manager.authenticate_user(username, password)


        
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Usuario o contraseña incorrectos",
                "username": username
            })
        
        # Crear sesión
        session_token = auth_manager.create_session_token(str(user.id))
        
        # Redirigir al dashboard con cookie de sesión
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=settings.session_expires_hours * 3600,
            httponly=True,
            secure=False,  # Cambiar a True en producción con HTTPS
            samesite="lax"
        )
        
        logger.info(f"Usuario logueado: {username}")
        return response

    @app.get("/logout", response_class=HTMLResponse)
    async def logout(request: Request):
        """Cerrar sesión"""
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("session_token")
        return response

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard(
        request: Request,
        page: int = 1,
        view: str = "monthly",  # monthly o historical
        user: User = Depends(require_auth)
    ):
        """Dashboard principal con lista de transacciones"""
        db = get_database()
        
        try:
            # Crear filtro base
            base_filter = {"user_id": ObjectId(str(user.id))}
            
            # Si es vista mensual, filtrar por mes actual
            if view == "monthly":
                from datetime import datetime
                now = datetime.now()
                start_of_month = datetime(now.year, now.month, 1)
                if now.month == 12:
                    end_of_month = datetime(now.year + 1, 1, 1)
                else:
                    end_of_month = datetime(now.year, now.month + 1, 1)
                
                base_filter["date"] = {
                    "$gte": start_of_month,
                    "$lt": end_of_month
                }
            
            # Obtener transacciones del usuario ordenadas por fecha descendente
            transactions_cursor = db.transactions.find(base_filter).sort("date", -1)
            transactions_list = list(transactions_cursor)
            
            # Paginar resultados
            per_page = 20
            transactions_page, pagination = paginate_list(transactions_list, page, per_page)
            
            # Crear resumen
            summary = TransactionSummary.from_transactions(transactions_list)
            
            # Preparar datos para gráficos
            chart_data = prepare_chart_data(transactions_list)
            
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user,
                "transactions": transactions_page,
                "summary": summary,
                "pagination": pagination,
                "current_view": view,
                "is_monthly": view == "monthly",
                "chart_data": chart_data
            })
            
        except Exception as e:
            logger.error(f"Error en dashboard: {e}")
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user,
                "transactions": [],
                "summary": TransactionSummary(),
                "pagination": {"page": 1, "pages": 1, "has_prev": False, "has_next": False},
                "current_view": view,
                "is_monthly": view == "monthly",
                "chart_data": {"categories": [], "colors": [], "amounts": []},
                "error": "Error cargando transacciones"
            })

    @app.get("/add-transaction", response_class=HTMLResponse)
    async def add_transaction_page(
        request: Request,
        user: User = Depends(require_auth)
    ):
        """Página para agregar nueva transacción"""
        return templates.TemplateResponse("add_transaction.html", {
            "request": request,
            "user": user,
            "transaction_types": TRANSACTION_TYPES,
            "transaction_origins": TRANSACTION_ORIGINS,
            "categories": COMMON_CATEGORIES,
            "error": None,
            "success": None
        })

    @app.post("/add-transaction", response_class=HTMLResponse)
    async def add_transaction_post(
        request: Request,
        amount: float = Form(...),
        transaction_type: str = Form(..., alias="type"),
        category: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        origin: Optional[str] = Form(None),
        metadata_json: Optional[str] = Form(None),
        date_str: Optional[str] = Form(None),
        user: User = Depends(require_auth)
    ):
        """Procesar nueva transacción"""
        db = get_database()
        
        try:
            # Validar tipo de transacción
            if transaction_type not in TRANSACTION_TYPES:
                raise ValueError("Tipo de transacción inválido")
            
            # Parsear fecha
            transaction_date = datetime.utcnow()
            if date_str:
                try:
                    transaction_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
                except ValueError:
                    pass  # Usar fecha actual si hay error
            
            # Validar metadata
            is_valid, metadata, error_msg = validate_metadata_json(metadata_json)
            if not is_valid:
                return templates.TemplateResponse("add_transaction.html", {
                    "request": request,
                    "user": user,
                    "transaction_types": TRANSACTION_TYPES,
                    "transaction_origins": TRANSACTION_ORIGINS,
                    "categories": COMMON_CATEGORIES,
                    "error": f"Error en metadatos: {error_msg}",
                    "form_data": {
                        "amount": amount,
                        "type": transaction_type,
                        "category": category,
                        "description": description,
                        "origin": origin,
                        "metadata_json": metadata_json
                    }
                })
            
            # Crear transacción
            transaction = Transaction(
                user_id=str(user.id),
                amount=amount,
                type=transaction_type,
                category=category or None,
                description=description or None,
                date=transaction_date,
                origin=origin or None,
                metadata=metadata
            )
            
            # Insertar en base de datos
            result = db.transactions.insert_one(transaction.model_dump(by_alias=True))
            
            logger.info(f"Transacción creada: {result.inserted_id} por usuario {user.username}")
            
            # Redirigir al dashboard con mensaje de éxito
            return RedirectResponse(url="/dashboard?success=transaction_added", status_code=302)
            
        except ValueError as e:
            return templates.TemplateResponse("add_transaction.html", {
                "request": request,
                "user": user,
                "transaction_types": TRANSACTION_TYPES,
                "transaction_origins": TRANSACTION_ORIGINS,
                "categories": COMMON_CATEGORIES,
                "error": str(e),
                "form_data": {
                    "amount": amount,
                    "type": transaction_type,
                    "category": category,
                    "description": description,
                    "origin": origin,
                    "metadata_json": metadata_json
                }
            })
            
        except Exception as e:
            logger.error(f"Error creando transacción: {e}")
            return templates.TemplateResponse("add_transaction.html", {
                "request": request,
                "user": user,
                "transaction_types": TRANSACTION_TYPES,
                "transaction_origins": TRANSACTION_ORIGINS,
                "categories": COMMON_CATEGORIES,
                "error": "Error interno del servidor",
                "form_data": {
                    "amount": amount,
                    "type": transaction_type,
                    "category": category,
                    "description": description,
                    "origin": origin,
                    "metadata_json": metadata_json
                }
            })

    @app.get("/transaction/{transaction_id}", response_class=HTMLResponse)
    async def view_transaction(
        request: Request,
        transaction_id: str,
        user: User = Depends(require_auth)
    ):
        """Ver detalles de una transacción específica"""
        db = get_database()
        
        try:
            # Verificar que el ObjectId sea válido
            if not ObjectId.is_valid(transaction_id):
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            
            # Buscar transacción que pertenezca al usuario
            transaction_doc = db.transactions.find_one({
                "_id": ObjectId(transaction_id),
                "user_id": ObjectId(str(user.id))
            })
            
            if not transaction_doc:
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            
            # Obtener mensaje de éxito si existe
            success_message = None
            if request.query_params.get("success") == "category_updated":
                success_message = "Categoría actualizada correctamente"
            
            return templates.TemplateResponse("transaction_detail.html", {
                "request": request,
                "user": user,
                "transaction": transaction_doc,
                "success_message": success_message,
                "categories": COMMON_CATEGORIES
            })
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error viendo transacción: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @app.post("/transaction/{transaction_id}/edit-category")
    async def edit_transaction_category(
        request: Request,
        transaction_id: str,
        category: str = Form(...),
        user: User = Depends(require_auth)
    ):
        """Editar la categoría de una transacción"""
        db = get_database()
        
        try:
            # Verificar que el ObjectId sea válido
            if not ObjectId.is_valid(transaction_id):
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            
            # Validar que la categoría sea válida
            if category not in COMMON_CATEGORIES:
                raise HTTPException(status_code=400, detail="Categoría no válida")
            
            # Actualizar la transacción
            result = db.transactions.update_one(
                {
                    "_id": ObjectId(transaction_id),
                    "user_id": ObjectId(str(user.id))
                },
                {
                    "$set": {
                        "category": category,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            
            # Redirigir de vuelta al detalle de la transacción con mensaje de éxito
            return RedirectResponse(
                url=f"/transaction/{transaction_id}?success=category_updated", 
                status_code=302
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error editando categoría de transacción: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @app.post("/validate-transaction/{transaction_id}")
    async def validate_transaction(
        request: Request,
        transaction_id: str,
        user: User = Depends(require_auth)
    ):
        """Valida manualmente una transacción (gasto)"""
        db = get_database()
        try:
            if not ObjectId.is_valid(transaction_id):
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            result = db.transactions.update_one(
                {
                    "_id": ObjectId(transaction_id),
                    "user_id": ObjectId(str(user.id)),
                    "type": "gasto"
                },
                {"$set": {"validated": True, "updated_at": datetime.utcnow()}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Transacción no encontrada o no es un gasto")
            return RedirectResponse(url="/dashboard?success=validated", status_code=302)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validando transacción: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    @app.post("/delete-transaction/{transaction_id}")
    async def delete_transaction(
        request: Request,
        transaction_id: str,
        user: User = Depends(require_auth)
    ):
        """Valida manualmente una transacción"""
        db = get_database()
        try:
            if not ObjectId.is_valid(transaction_id):
                raise HTTPException(status_code=404, detail="Transacción no encontrada")
            db.transactions.delete_one(
                {
                    "_id": ObjectId(transaction_id),
                    "user_id": ObjectId(str(user.id)),
                }
            )
            return RedirectResponse(url="/dashboard?success=deleted", status_code=302)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validando transacción: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    from pydantic import BaseModel
    class EmailWebhookRequest(BaseModel):
        subject: str
        body: str

    @app.post("/webhook/email")
    async def receive_email_webhook(
        subject: str = Form(..., description="Asunto del email"),
        body: str = Form(..., description="Contenido del email")
    ):
        """Endpoint para recibir emails via form data"""
        try:
            if not subject or not body:
                raise HTTPException(status_code=400, detail="Subject y body son requeridos")

            
            # Importar parsers
            # Intentar parsear con diferentes parsers
            transaction_data = None
            
            # Parser de Tenpo
            if TenpoEmailParser.can_parse(subject, body):
                transaction_data = TenpoEmailParser.parse(subject, body)
            
            if not transaction_data:
                # Log del email no parseado para debugging
                logger.info(f"Email no parseado - Subject: {subject[:50]}...")
                return {"status": "ignored", "reason": "No matching parser found"}

            
            # Aquí necesitarías obtener el user_id de alguna manera
            # Por ahora usaré un user_id por defecto o podrías pasarlo en el webhook
            # En un caso real, podrías usar el email del remitente para identificar al usuario
            default_user_id = "68ae0680e37dadbe6b948619"  # Cambiar por lógica real
            
            # Crear la transacción
            transaction = transaction_data.to_transaction(default_user_id)
            
            # Guardar en base de datos
            db = get_database()
            result = db.transactions.insert_one(transaction.model_dump(by_alias=True))
            
            logger.info(f"Transacción creada desde email: {result.inserted_id}")
            
            return {
                "status": "success", 
                "transaction_id": str(result.inserted_id),
                "amount": transaction.amount,
                "description": transaction.description
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error procesando webhook de email: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")


    # Ruta para health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            db = get_database()
            # Verificar conexión a la base de datos
            db.command("ping")
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")
