# utils.py
import re
import unicodedata
from typing import List, Dict, Any

def limpiar_texto(texto: str) -> str:
    """Limpiar y normalizar texto"""
    if not texto:
        return ""
    
    # Eliminar espacios extra
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    # Normalizar caracteres (acentos, etc.)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    
    return texto

def validar_email(email: str) -> bool:
    """Validar formato de email"""
    if not email:
        return False
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\$'
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    """Validar formato de teléfono chileno"""
    if not telefono:
        return False
    
    # Eliminar caracteres no numéricos
    telefono = re.sub(r'[^\d]', '', telefono)
    
    # Teléfono chileno: 9 dígitos (móvil) o 7-8 dígitos (fijo con código de área)
    return len(telefono) == 9 or (7 <= len(telefono) <= 8)

def normalizar_region(region: str) -> str:
    """Normalizar nombre de región chilena"""
    if not region:
        return ""
    
    region = limpiar_texto(region.lower())
    
    # Mapeo de regiones
    regiones_map = {
        'arica y parinacota': 'Arica y Parinacota',
        'tarapaca': 'Tarapacá',
        'antofagasta': 'Antofagasta',
        'atacama': 'Atacama',
        'coquimbo': 'Coquimbo',
        'valparaiso': 'Valparaíso',
        'metropolitana': 'Metropolitana',
        "o'higgins": "O'Higgins",
        'maule': 'Maule',
        '
