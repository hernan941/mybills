from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Maneja la conexión a MongoDB"""
    
    def __init__(self):
        self._client: MongoClient = None
        self._database: Database = None
    
    def connect(self) -> Database:
        """Establece conexión con MongoDB"""
        try:
            self._client = MongoClient(settings.mongodb_uri, server_api=ServerApi('1'))

            self._database = self._client[settings.database_name]
            
            # Verificar conexión
            self._client.admin.command('ping')
            logger.info(f"Conectado a MongoDB: {settings.database_name}")
            
            # Crear índices
            self._create_indexes()
            
            return self._database
            
        except Exception as e:
            logger.error(f"Error conectando a MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Crea índices necesarios para optimizar consultas"""
        try:
            # Índices para usuarios
            self._database.users.create_index("username", unique=True)
            self._database.users.create_index("email", unique=True)
            
            # Índices para transacciones
            self._database.transactions.create_index("user_id")
            self._database.transactions.create_index([("user_id", 1), ("date", -1)])
            self._database.transactions.create_index("date")
            
            logger.info("Índices creados correctamente")
            
        except Exception as e:
            logger.warning(f"Error creando índices: {e}")
    
    def close(self):
        """Cierra la conexión"""
        if self._client:
            self._client.close()
            logger.info("Conexión a MongoDB cerrada")
    
    @property
    def database(self) -> Database:
        """Retorna la instancia de la base de datos"""
        if self._database is None:
            return self.connect()
        return self._database

# Instancia global de conexión
db_connection = DatabaseConnection()

def get_database() -> Database:
    """Función helper para obtener la base de datos"""
    return db_connection.database

def close_database():
    """Función helper para cerrar la conexión"""
    db_connection.close()

def verify_collection_connection(collection_name: str = "users") -> bool:
    """Verifica la conexión a una colección específica"""
    try:
        db = get_database()
        count = db[collection_name].count_documents({})
        logger.info(f"Conexión verificada a la colección '{collection_name}', documentos: {count}")
        return True
    except Exception as e:
        logger.error(f"No se pudo conectar a la colección '{collection_name}': {e}")
        return False
