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
                        profesional.get('perfil_url'),
                        profesional.get('imagen'),
                        existing['id']
                    ))
                else:
                    # Insertar nuevo registro
                    conn.execute('''
                        INSERT INTO prevencionistas (
                            nombre, cargo, empresa, email, telefono, region,
                            especialidad, perfil_url, imagen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        profesional.get('nombre'),
                        profesional.get('cargo'),
                        profesional.get('empresa'),
                        profesional.get('email'),
                        profesional.get('telefono'),
                        profesional.get('region'),
                        profesional.get('especialidad'),
                        profesional.get('perfil_url'),
                        profesional.get('imagen')
                    ))
                
                count += 1
            
            # Registrar actualización
            conn.execute('''
                INSERT INTO actualizaciones (registros, detalles)
                VALUES (?, ?)
            ''', (count, f"Actualización masiva: {datetime.now().isoformat()}"))
            
            conn.commit()
            return count
        finally:
            conn.close()
    
    def get_profesionales(self, region='', especialidad='', search='', page=1, per_page=20):
        """Obtener profesionales con filtros y paginación"""
        conn = self._get_connection()
        try:
            # Construir consulta base
            query = "SELECT * FROM prevencionistas WHERE 1=1"
            params = []
            
            # Añadir filtros
            if region:
                query += " AND region LIKE ?"
                params.append(f"%{region}%")
            
            if especialidad:
                query += " AND especialidad LIKE ?"
                params.append(f"%{especialidad}%")
            
            if search:
                query += " AND (nombre LIKE ? OR empresa LIKE ? OR cargo LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
            # Contar total
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            total = conn.execute(count_query, params).fetchone()[0]
            
            # Añadir paginación
            query += " ORDER BY nombre LIMIT ? OFFSET ?"
            params.extend([per_page, (page - 1) * per_page])
            
            # Ejecutar consulta
            profesionales = conn.execute(query, params).fetchall()
            
            # Convertir a diccionarios
            result = []
            for p in profesionales:
                profesional = dict(p)
                # Eliminar campos internos si es necesario
                if 'creado_en' in profesional:
                    del profesional['creado_en']
                if 'actualizado_en' in profesional:
                    del profesional['actualizado_en']
                result.append(profesional)
            
            return total, result
        finally:
            conn.close()
    
    def get_statistics(self):
        """Obtener estadísticas de la base de datos"""
        conn = self._get_connection()
        try:
            # Total de profesionales
            total = conn.execute("SELECT COUNT(*) FROM prevencionistas").fetchone()[0]
            
            # Distribución por región
            regiones_query = """
                SELECT region, COUNT(*) as count 
                FROM prevencionistas 
                WHERE region IS NOT NULL AND region != ''
                GROUP BY region
                ORDER BY count DESC
            """
            regiones = dict(conn.execute(regiones_query).fetchall())
            
            # Distribución por especialidad
            especialidades_query = """
                SELECT especialidad, COUNT(*) as count 
                FROM prevencionistas 
                WHERE especialidad IS NOT NULL AND especialidad != ''
                GROUP BY especialidad
                ORDER BY count DESC
            """
            especialidades = dict(conn.execute(especialidades_query).fetchall())
            
            # Última actualización
            last_update = conn.execute(
                "SELECT timestamp FROM actualizaciones ORDER BY timestamp DESC LIMIT 1"
            ).fetchone()
            
            return {
                "total_profesionales": total,
                "regiones": regiones,
                "especialidades": especialidades,
                "ultima_actualizacion": last_update[0] if last_update else None
            }
        finally:
            conn.close()
    
    def get_regiones(self):
        """Obtener lista de regiones disponibles"""
        conn = self._get_connection()
        try:
            regiones = conn.execute("""
                SELECT DISTINCT region FROM prevencionistas 
                WHERE region IS NOT NULL AND region != ''
                ORDER BY region
            """).fetchall()
            return [r[0] for r in regiones]
        finally:
            conn.close()
    
    def get_especialidades(self):
        """Obtener lista de especialidades disponibles"""
        conn = self._get_connection()
        try:
            especialidades = conn.execute("""
                SELECT DISTINCT especialidad FROM prevencionistas 
                WHERE especialidad IS NOT NULL AND especialidad != ''
                ORDER BY especialidad
            """).fetchall()
            return [e[0] for e in especialidades]
        finally:
            conn.close()
    
    def update_last_update(self):
        """Registrar una actualización"""
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT INTO actualizaciones (registros, detalles)
                VALUES (?, ?)
            ''', (0, f"Actualización de timestamp: {datetime.now().isoformat()}"))
            conn.commit()
        finally:
            conn.close()
