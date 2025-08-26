import os

class Settings:
    """Configuración de la aplicación"""
    
    def __init__(self):
        self.mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/webmybills")
        self.secret_key: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
        self.database_name: str = self._extract_db_name(self.mongodb_uri)
        self.session_expires_hours: int = 24
        
    def _extract_db_name(self, uri: str) -> str:
        """Extrae el nombre de la base de datos de la URI"""
        try:
            # Para URIs como mongodb://localhost:27017/webmybills
            if "/" in uri:
                db_name = uri.split("/")[-1]
                # Remover parámetros de query si existen
                if "?" in db_name:
                    db_name = db_name.split("?")[0]
                return db_name if db_name else "webmybills"
            return "webmybills"
        except:
            return "webmybills"

# Instancia global de configuración
settings = Settings()

# Constantes de la aplicación
TRANSACTION_TYPES = [
    "gasto",
    "ingreso", 
    "transferencia"
]

TRANSACTION_ORIGINS = [
    "efectivo",
    "banco",
    "tarjeta_credito", 
    "tarjeta_debito",
    "transferencia_bancaria",
    "otro"
]

COMMON_CATEGORIES = [
    "alimentacion",
    "transporte",
    "entretenimiento",
    "salud",
    "educacion",
    "hogar",
    "trabajo",
    "compras",
    "servicios",
    "otro"
]
