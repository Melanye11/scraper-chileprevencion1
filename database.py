# database.py
import sqlite3
import json
from datetime import datetime
import os

class DatabaseManager:
    """Gestiona las operaciones de base de datos para prevencionistas"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get('DATABASE_URL', 'sqlite:///prevencionistas.db')
        self._init_db()
    
    def _get_connection(self):
        """Obtener conexión a la base de datos"""
        if self.db_path.startswith('sqlite'):
            conn = sqlite3.connect(self.db_path.replace('sqlite:///', ''))
            conn.row_factory = sqlite3.Row
            return conn
        # Aquí se podrían añadir otros tipos de conexión (PostgreSQL, MySQL, etc.)
        return None
    
    def _init_db(self):
        """Inicializar la base de datos si no existe"""
        conn = self._get_connection()
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prevencionistas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cargo TEXT,
                    empresa TEXT,
                    email TEXT,
                    telefono TEXT,
                    region TEXT,
                    especialidad TEXT,
                    perfil_url TEXT,
                    imagen TEXT,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS actualizaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registros INTEGER,
                    detalles TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_prevencionistas_region ON prevencionistas(region)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_prevencionistas_especialidad ON prevencionistas(especialidad)
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def save_profesionales(self, profesionales):
        """Guardar lista de profesionales en la base de datos"""
        conn = self._get_connection()
        try:
            # Contador de registros insertados/actualizados
            count = 0
            
            for profesional in profesionales:
                # Verificar si ya existe (por email o nombre + empresa)
                existing = None
                if profesional.get('email'):
                    existing = conn.execute(
                        'SELECT id FROM prevencionistas WHERE email = ?',
                        (profesional['email'],)
                    ).fetchone()
                
                if not existing and profesional.get('nombre') and profesional.get('empresa'):
                    existing = conn.execute(
                        'SELECT id FROM prevencionistas WHERE nombre = ? AND empresa = ?',
                        (profesional['nombre'], profesional['empresa'])
                    ).fetchone()
                
                if existing:
                    # Actualizar registro existente
                    conn.execute('''
                        UPDATE prevencionistas SET
                            cargo = ?, email = ?, telefono = ?, region = ?,
                            especialidad = ?, perfil_url = ?, imagen = ?,
                            actualizado_en = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (
                        profesional.get('cargo'),
                        profesional.get('email'),
                        profesional.get('telefono'),
                        profesional.get('region'),
                        profesional.get('especialidad'),
                        profesional
