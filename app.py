# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from scraper import ChilePrevencionScraper
from database import DatabaseManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Inicializar base de datos
db = DatabaseManager()

@app.route('/')
def index():
    """Renderizar la página principal"""
    return render_template('index.html')

@app.route('/api/prevencionistas', methods=['GET'])
def get_prevencionistas():
    """API para obtener prevencionistas con filtros y paginación"""
    try:
        # Parámetros de filtrado
        region = request.args.get('region', '')
        especialidad = request.args.get('especialidad', '')
        search = request.args.get('search', '')
        
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Obtener datos de la base de datos
        total, profesionales = db.get_profesionales(
            region=region,
            especialidad=especialidad,
            search=search,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            "total": total,
            "page": page,
            "per_page": per_page,
            "data": profesionales
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/actualizar', methods=['POST'])
def actualizar_datos():
    """Actualizar datos desde la web"""
    try:
        scraper = ChilePrevencionScraper()
        nuevos_datos = scraper.run()
        
        # Guardar en la base de datos
        count = db.save_profesionales(nuevos_datos)
        
        # Actualizar timestamp
        db.update_last_update()
        
        return jsonify({
            "message": "Datos actualizados correctamente",
            "total": count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Obtener estadísticas de los datos"""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regiones', methods=['GET'])
def get_regiones():
    """Obtener lista de regiones disponibles"""
    try:
        regiones = db.get_regiones()
        return jsonify({"regiones": regiones})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/especialidades', methods=['GET'])
def get_especialidades():
    """Obtener lista de especialidades disponibles"""
    try:
        especialidades = db.get_especialidades()
        return jsonify({"especialidades": especialidades})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
