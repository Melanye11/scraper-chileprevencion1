# models.py
from dataclasses import dataclass, asdict
from typing import Optional, List
import json

@dataclass
class Profesional:
    """Modelo para representar un profesional de prevención de riesgos"""
    nombre: str
    cargo: Optional[str] = None
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    region: Optional[str] = None
    especialidad: Optional[str] = None
    perfil_url: Optional[str] = None
    imagen: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Profesional':
        """Crear desde diccionario"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convertir a JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Profesional':
        """Crear desde JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

@dataclass
class Estadisticas:
    """Modelo para representar estadísticas de los datos"""
    total_profesionales: int
    regiones: dict
    especialidades: dict
    ultima_actualizacion: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Estadisticas':
        """Crear desde diccionario"""
        return cls(**data)
