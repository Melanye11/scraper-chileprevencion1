# scheduler.py
import schedule
import time
from datetime import datetime
import json
import os
from scraper import ChilePrevencionScraper

def update_data():
    print(f"Iniciando actualización de datos: {datetime.now()}")
    scraper = ChilePrevencionScraper()
    data = scraper.run()
    
    # Guardar timestamp de última actualización
    with open('last_update.json', 'w') as f:
        json.dump({"timestamp": datetime.now().isoformat()}, f)
    
    print(f"Actualización completada: {len(data)} registros")

def main():
    # Programar actualización diaria a las 2 AM
    schedule.every().day.at("02:00").do(update_data)
    
    # También actualizar cada 6 horas
    schedule.every(6).hours.do(update_data)
    
    print("Programador de actualizaciones iniciado")
    print("Próxima actualización programada para:", schedule.next_run())
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Comprobar cada minuto

if __name__ == "__main__":
    main()
