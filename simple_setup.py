#!/usr/bin/env python3
# Script simple para crear usuario sin usar modelos complejos

import os
import sys
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson import ObjectId

# Configuración
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/webmybills")
DATABASE_NAME = "webmybills"

def create_simple_user():
    """Crea un usuario simple directamente en MongoDB"""
    
    print("=== Creando usuario simple ===")
    
    try:
        # Conectar a MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Datos del usuario
        username = "admin"
        email = "admin@example.com" 
        password = "password123"
        
        # Verificar si ya existe
        existing = db.users.find_one({"username": username})
        if existing:
            print(f"✅ Usuario '{username}' ya existe con ID: {existing['_id']}")
            return existing['_id']
        
        # Hashear password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear documento de usuario
        user_doc = {
            "_id": ObjectId(),
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insertar en base de datos
        result = db.users.insert_one(user_doc)
        
        print(f"✅ Usuario creado exitosamente:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   ID: {result.inserted_id}")
        
        # Crear algunas transacciones de ejemplo
        create_sample_transactions(db, result.inserted_id)
        
        client.close()
        return result.inserted_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_sample_transactions(db, user_id):
    """Crea algunas transacciones de ejemplo"""
    
    print("\n=== Creando transacciones de ejemplo ===")
    
    sample_transactions = [
        {
            "_id": ObjectId(),
            "user_id": user_id,
            "amount": 1500.0,
            "type": "ingreso",
            "category": "trabajo",
            "description": "Salario del mes",
            "date": datetime.utcnow(),
            "origin": "transferencia_bancaria",
            "metadata": {"empresa": "TechCorp", "mes": "agosto"},
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user_id,
            "amount": 85.50,
            "type": "gasto",
            "category": "alimentacion",
            "description": "Compra semanal en supermercado",
            "date": datetime.utcnow(),
            "origin": "tarjeta_debito",
            "metadata": {"tienda": "Mercadona", "productos": 25},
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user_id,
            "amount": 45.0,
            "type": "gasto",
            "category": "transporte",
            "description": "Gasolina",
            "date": datetime.utcnow(),
            "origin": "tarjeta_credito",
            "metadata": {"gasolinera": "Repsol", "litros": 30},
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user_id,
            "amount": 650.0,
            "type": "pago",
            "category": "hogar",
            "description": "Alquiler del apartamento",
            "date": datetime.utcnow(),
            "origin": "transferencia_bancaria",
            "metadata": {"inmobiliaria": "CasaFacil", "mes": "agosto"},
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "user_id": user_id,
            "amount": 25.0,
            "type": "gasto",
            "category": "entretenimiento",
            "description": "Cine con amigos",
            "date": datetime.utcnow(),
            "origin": "efectivo",
            "metadata": {"pelicula": "Avatar 3", "personas": 2},
            "created_at": datetime.utcnow()
        }
    ]
    
    try:
        result = db.transactions.insert_many(sample_transactions)
        print(f"✅ {len(result.inserted_ids)} transacciones de ejemplo creadas")
        
        # Mostrar resumen
        total_ingresos = sum(t["amount"] for t in sample_transactions if t["type"] == "ingreso")
        total_gastos = sum(t["amount"] for t in sample_transactions if t["type"] == "gasto")
        total_pagos = sum(t["amount"] for t in sample_transactions if t["type"] == "pago")
        balance = total_ingresos - total_gastos - total_pagos
        
        print(f"\n📊 Resumen:")
        print(f"   Ingresos: €{total_ingresos:.2f}")
        print(f"   Gastos: €{total_gastos:.2f}")
        print(f"   Pagos: €{total_pagos:.2f}")
        print(f"   Balance: €{balance:.2f}")
        
    except Exception as e:
        print(f"⚠️  Error creando transacciones de ejemplo: {e}")

def test_connection():
    """Prueba la conexión a MongoDB"""
    
    print("=== Probando conexión a MongoDB ===")
    
    try:
        client = MongoClient(MONGODB_URI)
        # Ping a la base de datos
        client.admin.command('ping')
        print(f"✅ Conexión exitosa a: {MONGODB_URI}")
        
        # Mostrar bases de datos
        dbs = client.list_database_names()
        print(f"📋 Bases de datos disponibles: {dbs}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verificar que MongoDB esté ejecutándose")
        print("   2. Verificar la URI en el archivo .env")
        print("   3. Para MongoDB local: sudo systemctl start mongod")
        print("   4. Para MongoDB Atlas: verificar credenciales y red")
        return False

def main():
    """Función principal"""
    
    print("🚀 WebMyBills - Setup Simple")
    print("=" * 40)
    
    # Probar conexión primero
    if not test_connection():
        return
    
    print()
    
    # Crear usuario
    user_id = create_simple_user()
    
    if user_id:
        print(f"\n🎉 ¡Todo listo!")
        print(f"   Ya puedes iniciar la aplicación con: python main.py")
        print(f"   Usuario: admin")
        print(f"   Password: password123")
        print(f"   URL: http://localhost:8000")
    else:
        print(f"\n❌ No se pudo completar el setup")

if __name__ == "__main__":
    main()
