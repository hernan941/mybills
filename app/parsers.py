import re
from datetime import datetime
from typing import Optional, Dict, Any
from .models import TransactionCreate

class TenpoEmailParser:
    """Parser específico para emails de comprobantes de Tenpo"""
    
    TRIGGER_PHRASES = [
        "comprobante de compra exitosa",
        "la compra por",
        "fue exitosa"
    ]
    
    @classmethod
    def can_parse(cls, subject: str, body: str) -> bool:
        """Verifica si el email es un comprobante de Tenpo"""
        text = f"{subject} {body}".lower()
        print(text)
        return any(phrase in text for phrase in cls.TRIGGER_PHRASES)
    
    @classmethod
    def parse(cls, subject: str, body: str) -> Optional[TransactionCreate]:
        """Parsea el email y extrae los datos de la transacción"""
        if not cls.can_parse(subject, body):
            return None
        
        try:

            # Extraer monto
            amount = cls._extract_amount(body)
            if not amount:
                return None

            print("monto:", amount)
            
            # Extraer comercio/descripción

            description = cls._extract_merchant(body)


            print("descripcion:", description)
            
            category = cls._determine_category(description or "")

            print("category", category)
            
            # Extraer fecha
            transaction_date = cls._extract_date(body)

            
            print("transactiondateqw", transaction_date)
            
            # Crear metadata con información adicional
            metadata = cls._extract_metadata(body)

            print(metadata)
            
            return TransactionCreate(
                amount=amount,
                type="gasto",
                category=category,
                description=description or "Compra con tarjeta Tenpo",
                date=transaction_date,
                origin="tenpo",
                metadata_json=str(metadata) if metadata else None
            )
        
        except Exception as e:
            print(f"Error parsing Tenpo email: {e}")
            return None

    @classmethod
    def _determine_category(cls, merchant_name: str) -> str:
        """Determina la categoría basándose en el nombre del comercio"""
        if not merchant_name:
            return "otros"
        
        merchant_lower = merchant_name.lower()
        
        # Supermercados y tiendas de comida
        supermarket_keywords = [
            'unimarc', 'jumbo', 'santa isabel', 'lider', 'tottus', 'ekono',
            'supermercado', 'minimarket', 'almacen', 'market', 'super'
        ]
        
        # Restaurantes y comida
        food_keywords = [
            'restaurant', 'resto', 'pizz', 'burger', 'mcdon', 'kfc', 'subway',
            'cafe', 'coffee', 'starbucks', 'domin', 'papa john', 'sushi',
            'comida', 'food', 'bar ', 'pub ', 'delivery'
        ]
        
        # Transporte
        transport_keywords = [
            'uber', 'taxi', 'cabify', 'didi', 'bus', 'metro', 'transporte',
            'estacion', 'peaje', 'parking', 'estacionamiento', 'bencina',
            'copec', 'shell', 'esso', 'petrobras', 'combustible'
        ]
        
        # Entretenimiento
        entertainment_keywords = [
            'cine', 'cinema', 'netflix', 'spotify', 'amazon', 'disney',
            'game', 'steam', 'playstation', 'xbox', 'teatro', 'concierto',
            'mall', 'plaza', 'shopping'
        ]
        
        # Salud
        health_keywords = [
            'farmacia', 'pharmacy', 'cruz verde', 'salcobrand', 'ahumada',
            'hospital', 'clinica', 'medic', 'doctor', 'dental', 'optica',
            'laboratorio', 'isapre', 'fonasa'
        ]
        
        # Servicios
        services_keywords = [
            'banco', 'bank', 'atm', 'cajero', 'notaria', 'abogad',
            'servicio', 'reparacion', 'mantenci', 'tecnico', 'install'
        ]
        
        # Ropa y accesorios
        clothing_keywords = [
            'ropa', 'clothing', 'fashion', 'moda', 'zapato', 'calzado',
            'adidas', 'nike', 'zara', 'h&m', 'falabella', 'ripley',
            'paris', 'corona', 'hites'
        ]
        
        # Educación
        education_keywords = [
            'universidad', 'instituto', 'colegio', 'escuela', 'educacion',
            'curso', 'capacitacion', 'libreria', 'papeleria'
        ]
        
        # Verificar categorías en orden de prioridad
        if any(keyword in merchant_lower for keyword in supermarket_keywords):
            return "supermercado"
        elif any(keyword in merchant_lower for keyword in food_keywords):
            return "restaurantes"
        elif any(keyword in merchant_lower for keyword in transport_keywords):
            return "transporte"
        elif any(keyword in merchant_lower for keyword in health_keywords):
            return "salud"
        elif any(keyword in merchant_lower for keyword in entertainment_keywords):
            return "entretenimiento"
        elif any(keyword in merchant_lower for keyword in clothing_keywords):
            return "ropa"
        elif any(keyword in merchant_lower for keyword in education_keywords):
            return "educacion"
        elif any(keyword in merchant_lower for keyword in services_keywords):
            return "servicios"
        else:
            return "otros"
    
    @classmethod
    def _extract_amount(cls, body: str) -> Optional[float]:
        """Extrae el monto de la transacción"""
        # Buscar patrones como "$8.034" o "Monto transacción: $8.034"
        patterns = [
            r'monto transacci[óo]n:\s*\$([0-9.,]+)',
            r'la compra por \$([0-9.,]+)',
            r'\$([0-9.,]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    @classmethod
    def _extract_merchant(cls, body: str) -> Optional[str]:
            """Extrae el nombre del comercio"""
            # Buscar patrón "comercio: NOMBRE_COMERCIO" con más flexibilidad
            patterns = [
                r'comercio:\s*([^\n\r]+?)(?:\s+cuotas:|$)',  # Buscar hasta "cuotas:" o fin
                r'comercio:\s+([^0-9\n\r]+?)(?:\s+\d|$)',    # Buscar hasta número o fin
                r'comercio:\s*([^\n\r]{3,50}?)(?:\s+cuotas|\s+fecha|$)',  # Más específico
                r'comercio:\s*([a-zA-Z\s]+[a-zA-Z]+)',       # Solo letras y espacios
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    merchant = match.group(1).strip()
                    # Limpiar caracteres extraños y normalizar espacios
                    merchant = re.sub(r'\s+', ' ', merchant)
                    merchant = re.sub(r'[^\w\s\-]', '', merchant)  # Remover caracteres especiales
                    if len(merchant) > 3:  # Validar que tenga contenido útil
                        return merchant[:200] if len(merchant) > 200 else merchant
            
            return None

    
    @classmethod
    def _extract_date(cls, body: str) -> Optional[datetime]:
        """Extrae la fecha de la transacción"""
        # Buscar patrón "Fecha: 15-08-2025" y "Hora: 16:24:00"
        date_pattern = r'fecha:\s*(\d{2}-\d{2}-\d{4})'
        time_pattern = r'hora:\s*(\d{2}:\d{2}:\d{2})'
        
        date_match = re.search(date_pattern, body, re.IGNORECASE)
        time_match = re.search(time_pattern, body, re.IGNORECASE)
        
        if date_match:
            date_str = date_match.group(1)
            time_str = time_match.group(1) if time_match else "00:00:00"
            
            try:
                return datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M:%S")
            except ValueError:
                pass
        
        return datetime.now()
    
    @classmethod
    def _extract_metadata(cls, body: str) -> Dict[str, Any]:
        """Extrae metadata adicional del email"""
        metadata = {}
        
        # Extraer código de transacción - patrón más flexible
        code_patterns = [
            r'c[óo]digo\s+de\s+transacci[óo]n:\s*([^\s\n\r]+)',
            r'c[óo]digo:\s*([^\s\n\r]+)',
            r'transacci[óo]n:\s*([0-9]+)'
        ]
        
        for pattern in code_patterns:
            code_match = re.search(pattern, body, re.IGNORECASE)
            if code_match:
                metadata['transaction_code'] = code_match.group(1).strip()
                break
        
        # Extraer cuotas - patrón más flexible para manejar espacios/tabs
        cuotas_patterns = [
            r'cuotas:\s*(\d+)',
            r'cuotas\s+(\d+)',
            r'cuota:\s*(\d+)'
        ]
        
        for pattern in cuotas_patterns:
            cuotas_match = re.search(pattern, body, re.IGNORECASE)
            if cuotas_match:
                metadata['installments'] = int(cuotas_match.group(1))
                break
        
        metadata['source'] = 'tenpo_email'
        return metadata
