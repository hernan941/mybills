from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
import json

# Tipo personalizado para ObjectId
PyObjectId = Annotated[str, Field(..., description="MongoDB ObjectId as string")]

def validate_object_id(v):
    """Valida que sea un ObjectId válido"""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")

class User(BaseModel):
    """Modelo de Usuario"""
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "username": "usuario123",
                "email": "usuario@example.com",
                "password_hash": "$2b$12$...",
                "is_active": True
            }
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId")
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str = Field(...)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if v is None:
            return str(ObjectId())  # Generar nuevo ObjectId si no existe
        return validate_object_id(v)

    def model_dump(self, **kwargs):
        """Override model_dump para manejar ObjectId correctamente"""
        data = super().model_dump(**kwargs)
        if "_id" in data and data["_id"] is not None:
            data["_id"] = ObjectId(data["_id"]) if kwargs.get('by_alias') else str(data["_id"])
        return data

    def dict(self, **kwargs):
        """Mantener compatibilidad con dict()"""
        return self.model_dump(**kwargs)

class Transaction(BaseModel):
    """Modelo de Transacción"""
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "amount": 25.50,
                "type": "gasto",
                "category": "alimentacion",
                "description": "Compra en supermercado",
                "origin": "tarjeta_debito",
                "validated": True,
                "metadata": {"tienda": "Mercadona", "productos": 5}
            }
        }
    )
    
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id", description="MongoDB ObjectId")
    user_id: str = Field(..., description="MongoDB ObjectId del usuario")
    amount: float = Field(..., gt=0, description="Monto de la transacción")
    type: str = Field(..., description="Tipo: gasto, ingreso, transferencia")
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: datetime = Field(default_factory=datetime.utcnow)
    origin: Optional[str] = Field(None, description="Origen: efectivo, banco, tarjeta, etc.")
    validated: bool = False
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if v is None:
            return str(ObjectId())  # Generar nuevo ObjectId si no existe
        return validate_object_id(v)

    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        return validate_object_id(v)

    def model_dump(self, **kwargs):
        """Override model_dump para manejar ObjectId correctamente"""
        data = super().model_dump(**kwargs)
        if kwargs.get('by_alias'):
            # Para guardar en MongoDB, convertir a ObjectId
            if "_id" in data and data["_id"] is not None:
                data["_id"] = ObjectId(data["_id"])
            if "user_id" in data:
                data["user_id"] = ObjectId(data["user_id"])
        return data

    def dict(self, **kwargs):
        """Mantener compatibilidad con dict()"""
        return self.model_dump(**kwargs)

class TransactionCreate(BaseModel):
    """Modelo para crear transacciones (sin campos auto-generados)"""
    
    amount: float = Field(..., gt=0)
    type: str = Field(...)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = Field(None)
    origin: Optional[str] = Field(None)
    metadata_json: Optional[str] = Field(None, description="JSON string de metadata")

    def to_transaction(self, user_id: str) -> Transaction:
        """Convierte a objeto Transaction completo"""
        # Parsear metadata si existe
        metadata = {}
        if self.metadata_json:
            try:
                metadata = json.loads(self.metadata_json)
            except json.JSONDecodeError:
                metadata = {"raw": self.metadata_json}
        
        return Transaction(
            user_id=user_id,
            amount=self.amount,
            type=self.type,
            category=self.category,
            description=self.description,
            date=self.date or datetime.now(),
            updated_at=datetime.now(),
            origin=self.origin,
            metadata=metadata
        )

class TransactionSummary(BaseModel):
    """Resumen de transacciones para el dashboard"""
    
    total_ingresos: float = 0.0
    total_gastos: float = 0.0
    total_transferencias: float = 0.0
    balance: float = 0.0
    count_transactions: int = 0
    
    @classmethod
    def from_transactions(cls, transactions: list) -> 'TransactionSummary':
        """Crea resumen desde lista de transacciones"""
        summary = cls()
        
        for tx in transactions:
            summary.count_transactions += 1
            amount = tx.get('amount', 0)
            tx_type = tx.get('type', '').lower()
            
            if tx_type == 'ingreso':
                summary.total_ingresos += amount
            elif tx_type == 'gasto':
                summary.total_gastos += amount
        
        # El balance es ingresos menos todo lo demás
        summary.balance = (summary.total_ingresos - 
                          summary.total_gastos)
        
        return summary
