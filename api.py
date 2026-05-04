
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import pandas as pd
from scraper import ChilePrevencionScraper

app = Flask(__name__)
CORS(app)

# Ruta principal
@app.route('/')
def index():
    return jsonify({
        "message": "API de Prevencionistas de Riego en Chile",
        "version": "1.0.0",
        "endpoints": [
            "/api/prevencionistas - Obtener todos los prevencionistas",
            "/api/prevencionistas?region=nombre - Filtrar por región",
            "/api/prevencionistas?especialidad=nombre - Filtrar por especialidad",
            "/api/actualizar - Actualizar datos desde la web",
            "/api/estadisticas - Estadísticas de los datos"
        ]
    })

# Obtener todos los prevencionistas
@app.route('/api/prevencionistas', methods=['GET'])
def get_prevencionistas():
    try:
        # Parámetros de filtrado
        region = request.args.get('region')
        especialidad = request.args.get('especialidad')
        
        # Cargar datos
        if os.path.exists('prevencionistas_chile.json'):
            with open('prevencionistas_chile.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Aplicar filtros si se proporcionan
        if region:
            data = [p for p in data if 'region' in p and region.lower() in p['region'].lower()]
        
        if especialidad:
            data = [p for p in data if 'especialidad' in p and especialidad.lower() in p['especialidad'].lower()]
        
        # Paginación
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_data = data[start:end]
        
        return jsonify({
            "total": len(data),
            "page": page,
            "per_page": per_page,
            "data": paginated_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar datos desde la web
@app.route('/api/actualizar', methods=['POST'])
def actualizar_datos():
    try:
        scraper = ChilePrevencionScraper()
        data = scraper.run()
        return jsonify({
            "message": "Datos actualizados correctamente",
            "total": len(data),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Estadísticas de los datos
@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    try:
        if os.path.exists('prevencionistas_chile.json'):
            with open('prevencionistas_chile.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Calcular estadísticas
        total = len(data)
        regiones = {}
        especialidades = {}
        
        for profesional in data:
            # Contar por región
            if 'region' in profesional:
                region = profesional['region']
                regiones[region] = regiones.get(region, 0) + 1
            
            # Contar por especialidad
            if 'especialidad' in profesional:
                especialidad = profesional['especialidad']
                especialidades[especialidad] = especialidades.get(especialidad, 0) + 1
        
        return jsonify({
            "total_profesionales": total,
            "regiones": regiones,
            "especialidades": especialidades,
            "ultima_actualizacion": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
