import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from itsdangerous import URLSafeTimedSerializer
from app.config import settings
from app.database import get_database
from app.models import User
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Maneja autenticación y sesiones"""
    
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(settings.secret_key)
        self.db = get_database()
    
    def hash_password(self, password: str) -> str:
        """Hashea una contraseña"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autentica un usuario con username y password"""
        try:
            # Buscar usuario por username
            user_doc = self.db.users.find_one({"username": username, "is_active": True})
            
            if not user_doc:
                logger.info(f"Usuario no encontrado: {username}")
                return None
            
            # Verificar contraseña
            if self.verify_password(password, user_doc["password_hash"]):
                # Convertir a modelo User
                user = User(**user_doc)
                logger.info(f"Usuario autenticado correctamente: {username}")
                return user
            else:
                logger.info(f"Contraseña incorrecta para usuario: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return None
    
    def create_session_token(self, user_id: str) -> str:
        """Crea un token de sesión seguro"""
        data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=settings.session_expires_hours)).isoformat()
        }
        return self.serializer.dumps(data)
    
    def verify_session_token(self, token: str) -> Optional[str]:
        """Verifica un token de sesión y retorna el user_id si es válido"""
        try:
            # Verificar token (incluye verificación de tiempo)
            data = self.serializer.loads(
                token, 
                max_age=settings.session_expires_hours * 3600  # en segundos
            )
            
            user_id = data.get("user_id")
            expires_at = datetime.fromisoformat(data.get("expires_at"))
            
            # Verificar que no haya expirado
            if datetime.utcnow() > expires_at:
                logger.info("Token de sesión expirado")
                return None
            
            # Verificar que el usuario aún existe y está activo
            user_doc = self.db.users.find_one({
                "_id": ObjectId(user_id),
                "is_active": True
            })
            
            if not user_doc:
                logger.info(f"Usuario no encontrado o inactivo: {user_id}")
                return None
            
            return user_id
            
        except Exception as e:
            logger.error(f"Error verificando token de sesión: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        try:
            user_doc = self.db.users.find_one({
                "_id": ObjectId(user_id),
                "is_active": True
            })
            
            if user_doc:
                return User(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Crea un nuevo usuario"""
        try:
            # Verificar que no exista el username o email
            existing = self.db.users.find_one({
                "$or": [
                    {"username": username},
                    {"email": email}
                ]
            })
            
            if existing:
                logger.info(f"Usuario o email ya existe: {username}, {email}")
                return None
            
            # Crear usuario
            password_hash = self.hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            # Insertar en base de datos
            result = self.db.users.insert_one(user.model_dump(by_alias=True))
            user.id = result.inserted_id
            
            logger.info(f"Usuario creado correctamente: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            return None

# Instancia global del manejador de autenticación
auth_manager = AuthManager()

def get_current_user_id(session_token: str) -> Optional[str]:
    """Función helper para obtener el ID del usuario actual desde el token de sesión"""
    return auth_manager.verify_session_token(session_token)

def get_current_user(session_token: str) -> Optional[User]:
    """Función helper para obtener el usuario actual desde el token de sesión"""
    user_id = get_current_user_id(session_token)
    if user_id:
        return auth_manager.get_user_by_id(user_id)
    return None
