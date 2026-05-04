# config.py
import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-prevencionistas'
    
    # Configuración de la base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///prevencionistas.db'
    
    # Configuración de scraping
    SCRAPE_INTERVAL = int(os.environ.get('SCRAPE_INTERVAL', 6))  # horas
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
    
    # Configuración de paginación
    DEFAULT_PER_PAGE = int(os.environ.get('DEFAULT_PER_PAGE', 20))
    MAX_PER_PAGE = int(os.environ.get('MAX_PER_PAGE', 100))
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Configuración de logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
