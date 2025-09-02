from datetime import datetime
from typing import Optional, List
import json
import logging

logger = logging.getLogger(__name__)

def get_current_month_name(include_year: bool = True) -> str:
    """Retorna el nombre del mes actual en español"""
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    now = datetime.now()
    if include_year:
        return f"{months[now.month]} {now.year}"
    else:
        return months[now.month]

def format_currency(amount: float) -> str:
    """Formatea un monto como moneda"""
    return f"${amount:,.2f}"

def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Formatea una fecha/hora"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    return dt.strftime(format_str)

def format_date(dt: datetime, format_str: str = "%d/%m/%Y") -> str:
    """Formatea solo la fecha"""
    return format_datetime(dt, format_str)

def safe_json_loads(json_str: Optional[str]) -> dict:
    """Parsea JSON de forma segura, retorna dict vacío si falla"""
    if not json_str:
        return {}
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def safe_json_dumps(data: dict) -> str:
    """Convierte dict a JSON de forma segura"""
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return "{}"

def get_transaction_type_color(transaction_type: str) -> str:
    """Retorna una clase CSS para el color según el tipo de transacción"""
    colors = {
        "ingreso": "text-success",
        "gasto": "text-danger", 
        "transferencia": "text-info"
    }
    return colors.get(transaction_type.lower(), "text-secondary")

def get_transaction_type_icon(transaction_type: str) -> str:
    """Retorna un icono para el tipo de transacción"""
    icons = {
        "ingreso": "↗️",
        "gasto": "↘️",
        "transferencia": "🔄"
    }
    return icons.get(transaction_type.lower(), "💰")

def humanize_origin(origin: Optional[str]) -> str:
    """Convierte el origen técnico a formato legible"""
    if not origin:
        return "No especificado"
    
    mapping = {
        "efectivo": "Efectivo",
        "banco": "Banco",
        "tarjeta_credito": "Tarjeta de Crédito",
        "tarjeta_debito": "Tarjeta de Débito", 
        "transferencia_bancaria": "Transferencia Bancaria",
        "tenpo": "Tenpo",
        "otro": "Otro"
    }
    return mapping.get(origin, origin.replace("_", " ").title())

def humanize_category(category: Optional[str]) -> str:
    """Convierte la categoría técnica a formato legible"""
    if not category:
        return "Sin categoría"
        
    mapping = {
        "alimentacion": "Alimentación",
        "transporte": "Transporte",
        "entretenimiento": "Entretenimiento",
        "salud": "Salud",
        "educacion": "Educación",
        "hogar": "Hogar",
        "trabajo": "Trabajo",
        "compras": "Compras",
        "servicios": "Servicios",
        "supermercado": "Supermercado",
        "restaurantes": "Restaurantes",
        "ropa": "Ropa y Accesorios",
        "otros": "Otros",
        "otro": "Otro"  # Mantener compatibilidad hacia atrás
    }
    return mapping.get(category, category.replace("_", " ").title())

def humanize_transaction_type(transaction_type: str) -> str:
    """Convierte el tipo de transacción a formato legible"""
    mapping = {
        "gasto": "Gasto",
        "ingreso": "Ingreso",
        "transferencia": "Transferencia"
    }
    return mapping.get(transaction_type.lower(), transaction_type.title())

def validate_metadata_json(metadata_str: Optional[str]) -> tuple[bool, dict, str]:
    """
    Valida una cadena JSON de metadata.
    Retorna: (es_valido, dict_parseado, mensaje_error)
    """
    if not metadata_str or metadata_str.strip() == "":
        return True, {}, ""
    
    try:
        parsed = json.loads(metadata_str)
        if not isinstance(parsed, dict):
            return False, {}, "Los metadatos deben ser un objeto JSON válido"
        return True, parsed, ""
    except json.JSONDecodeError as e:
        return False, {}, f"JSON inválido: {str(e)}"

def paginate_list(items: List, page: int = 1, per_page: int = 20) -> tuple[List, dict]:
    """
    Pagina una lista de elementos.
    Retorna: (items_paginados, info_paginacion)
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    items_page = items[start:end]
    
    pagination_info = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page,
        "has_prev": page > 1,
        "has_next": end < total,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if end < total else None
    }
    
    return items_page, pagination_info

def truncate_text(text: Optional[str], max_length: int = 50) -> str:
    """Trunca texto si es muy largo"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_month_name(month: int) -> str:
    """Retorna el nombre del mes en español"""
    months = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return months[month] if 1 <= month <= 12 else str(month)
