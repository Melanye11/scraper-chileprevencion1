import re
import unicodedata
import json
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
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
        'biobio': 'Biobío',
        'araucania': 'Araucanía',
        'los rios': 'Los Ríos',
        'los lagos': 'Los Lagos',
        'aysen': 'Aysén',
        'magallanes': 'Magallanes'
    }
    
    # Buscar coincidencia
    for key, value in regiones_map.items():
        if key in region:
            return value
    
    return region.title() if region else ""

def extraer_informacion_contacto(texto: str) -> Dict[str, str]:
    """Extraer emails y teléfonos de un texto"""
    resultado = {'emails': [], 'telefonos': []}
    
    if not texto:
        return resultado
    
    # Extraer emails
    email_patron = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    resultado['emails'] = re.findall(email_patron, texto)
    
    # Extraer teléfonos (formato chileno)
    telefono_patron = r'\b(?:\+?56)?(?:9\d{8}|2\d{7}|[3-8]\d{6})\b'
    telefonos = re.findall(telefono_patron, texto)
    
    # Formatear teléfonos
    resultado['telefonos'] = []
    for telefono in telefonos:
        # Eliminar prefijo 56 si existe
        if telefono.startswith('56'):
            telefono = telefono[2:]
        
        # Asegurar formato de 9 dígitos para móviles
        if len(telefono) == 8 and telefono.startswith('9'):
            telefono = telefono[:0] + '9' + telefono
        
        resultado['telefonos'].append(telefono)
    
    return resultado

def generar_slug(texto: str) -> str:
    """Generar slug a partir de texto"""
    if not texto:
        return ""
    
    # Normalizar y eliminar caracteres especiales
    texto = limpiar_texto(texto.lower())
    texto = re.sub(r'[^\w\s-]', '', texto)
    
    # Reemplazar espacios con guiones
    return re.sub(r'[-\s]+', '-', texto)

def paginar_resultados(datos: List[Any], pagina: int, por_pagina: int) -> Dict[str, Any]:
    """Paginar una lista de resultados"""
    total = len(datos)
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    
    return {
        'total': total,
        'pagina': pagina,
        'por_pagina': por_pagina,
        'total_paginas': (total + por_pagina - 1) // por_pagina,
        'datos': datos[inicio:fin]
    }

def exportar_a_json(datos: List[Dict], nombre_archivo: str) -> bool:
    """Exportar datos a archivo JSON"""
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error al exportar a JSON: {e}")
        return False

def exportar_a_csv(datos: List[Dict], nombre_archivo: str) -> bool:
    """Exportar datos a archivo CSV"""
    try:
        import csv
        
        if not datos:
            return False
        
        campos = list(datos[0].keys())
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
        
        return True
    except Exception as e:
        print(f"Error al exportar a CSV: {e}")
        return False
