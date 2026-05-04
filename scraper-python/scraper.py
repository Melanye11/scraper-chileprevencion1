import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import json
import pandas as pd
from urllib.parse import urljoin
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class ChilePrevencionScraper:
    def __init__(self):
        self.base_url = "https://chileprevencion.cl"
        self.ua = UserAgent()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-CL,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
        # Configuración de Selenium para sitios con JavaScript
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument(f"--user-agent={self.ua.random}")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
    def setup_selenium_driver(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def get_page_with_selenium(self, url):
        driver = self.setup_selenium_driver()
        try:
            driver.get(url)
            # Esperar a que la página cargue completamente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Simular comportamiento humano con scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))
            page_source = driver.page_source
            return page_source
        except TimeoutException:
            print(f"Timeout al cargar {url}")
            return None
        finally:
            driver.quit()
    
    def get_page_with_requests(self, url):
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error {response.status_code} al acceder a {url}")
                return None
        except Exception as e:
            print(f"Error al hacer la petición: {e}")
            return None
    
    def extract_professionals_info(self, html_content):
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        professionals = []
        
        # Intentar diferentes selectores según la estructura del sitio
        possible_selectors = [
            '.professional-card',
            '.member-card',
            '.profile-card',
            '.prevencionista-item',
            '.team-member',
            '.staff-member',
            '.directory-item',
            '.contact-card',
            '.person-card',
            'article[class*="member"]',
            'article[class*="professional"]',
            'div[class*="profile"]',
            'li[class*="member"]',
            'li[class*="professional"]'
        ]
        
        for selector in possible_selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Se encontraron {len(cards)} elementos con el selector: {selector}")
                break
        
        if not cards:
            # Intentar encontrar enlaces a perfiles individuales
            profile_links = soup.select('a[href*="perfil"], a[href*="member"], a[href*="profesional"]')
            if profile_links:
                print(f"Se encontraron {len(profile_links)} enlaces a perfiles individuales")
                for link in profile_links[:10]:  # Limitar a 10 para evitar sobrecarga
                    profile_url = urljoin(self.base_url, link['href'])
                    profile_html = self.get_page_with_requests(profile_url) or self.get_page_with_selenium(profile_url)
                    if profile_html:
                        profile_info = self.extract_profile_details(profile_html)
                        if profile_info:
                            professionals.append(profile_info)
                    time.sleep(random.uniform(1, 3))
                return professionals
        
        # Extraer información de las tarjetas encontradas
        for card in cards:
            professional = {}
            
            # Extraer nombre
            name_selectors = ['h1', 'h2', 'h3', '.name', '.professional-name', '.member-name', '.title']
            for selector in name_selectors:
                name_elem = card.select_one(selector)
                if name_elem:
                    professional['nombre'] = name_elem.get_text(strip=True)
                    break
            
            # Extraer cargo/título
            title_selectors = ['.position', '.title', '.role', '.professional-title', '.job-title']
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    professional['cargo'] = title_elem.get_text(strip=True)
                    break
            
            # Extraer empresa
            company_selectors = ['.company', '.organization', '.employer', '.workplace']
            for selector in company_selectors:
                company_elem = card.select_one(selector)
                if company_elem:
                    professional['empresa'] = company_elem.get_text(strip=True)
                    break
            
            # Extraer email
            email_elem = card.select_one('a[href^="mailto:"]')
            if email_elem:
                professional['email'] = email_elem.get('href').replace('mailto:', '')
            
            # Extraer teléfono
            phone_selectors = ['a[href^="tel:"]', '.phone', '.telephone', '.contact-phone']
            for selector in phone_selectors:
                phone_elem = card.select_one(selector)
                if phone_elem:
                    phone_text = phone_elem.get_text(strip=True)
                    if phone_text:
                        professional['telefono'] = phone_text
                        break
            
            # Extraer región
            region_selectors = ['.region', '.location', '.area', '.zone']
            for selector in region_selectors:
                region_elem = card.select_one(selector)
                if region_elem:
                    professional['region'] = region_elem.get_text(strip=True)
                    break
            
            # Extraer especialidad
            specialty_selectors = ['.specialty', '.expertise', '.specialization', '.area-focus']
            for selector in specialty_selectors:
                specialty_elem = card.select_one(selector)
                if specialty_elem:
                    professional['especialidad'] = specialty_elem.get_text(strip=True)
                    break
            
            # Extraer enlace al perfil
            profile_link = card.select_one('a[href]')
            if profile_link:
                professional['perfil_url'] = urljoin(self.base_url, profile_link.get('href'))
            
            if professional.get('nombre'):  # Solo añadir si tiene nombre
                professionals.append(professional)
        
        return professionals
    
    def extract_profile_details(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        profile = {}
        
        # Extraer información detallada del perfil
        name_elem = soup.select_one('h1, .profile-name, .member-name')
        if name_elem:
            profile['nombre'] = name_elem.get_text(strip=True)
        
        # Extraer información de contacto
        email_elem = soup.select_one('a[href^="mailto:"]')
        if email_elem:
            profile['email'] = email_elem.get('href').replace('mailto:', '')
        
        phone_elem = soup.select_one('a[href^="tel:"], .phone, .telephone')
        if phone_elem:
            profile['telefono'] = phone_elem.get_text(strip=True)
        
        # Extraer información profesional
        title_elem = soup.select_one('.position, .title, .role')
        if title_elem:
            profile['cargo'] = title_elem.get_text(strip=True)
        
        company_elem = soup.select_one('.company, .organization')
        if company_elem:
            profile['empresa'] = company_elem.get_text(strip=True)
        
        region_elem = soup.select_one('.region, .location')
        if region_elem:
            profile['region'] = region_elem.get_text(strip=True)
        
        return profile if profile.get('nombre') else None
    
    def search_directory(self):
        # URL de búsqueda o directorio del sitio
        search_urls = [
            f"{self.base_url}/directorio",
            f"{self.base_url}/profesionales",
            f"{self.base_url}/prevencionistas",
            f"{self.base_url}/miembros",
            f"{self.base_url}/busqueda"
        ]
        
        all_professionals = []
        
        for url in search_urls:
            print(f"Intentando acceder a: {url}")
            
            # Primero
            html_content = self.get_page_with_requests(url)
            
            # Si falla, intentar con Selenium
            if not html_content:
                print("Falló con requests, intentando con Selenium...")
                html_content = self.get_page_with_selenium(url)
            
            if html_content:
                professionals = self.extract_professionals_info(html_content)
                if professionals:
                    all_professionals.extend(professionals)
                    print(f"Se extrajeron {len(professionals)} profesionales de {url}")
                else:
                    print("No se encontraron profesionales en esta página")
                
                # Intentar paginación
                self.extract_paginated_results(url, all_professionals)
            else:
                print(f"No se pudo acceder a {url}")
            
            # Pausa entre peticiones para no ser bloqueado
            time.sleep(random.uniform(2, 5))
        
        return all_professionals
    
    def extract_paginated_results(self, base_url, professionals_list):
        # Intentar encontrar enlaces de paginación
        pagination_selectors = [
            '.pagination a',
            '.paging a',
            '.page-nav a',
            'a[href*="page"]',
            'a[href*="pagina"]'
        ]
        
        html_content = self.get_page_with_requests(base_url) or self.get_page_with_selenium(base_url)
        if not html_content:
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for selector in pagination_selectors:
            page_links = soup.select(selector)
            if page_links:
                print(f"Se encontró paginación con {len(page_links)} páginas")
                # Extraer números de página
                page_numbers = set()
                for link in page_links:
                    href = link.get('href', '')
                    # Extraer número de página del href
                    page_match = re.search(r'page[=/](\d+)', href) or re.search(r'pagina[=/](\d+)', href)
                    if page_match:
                        page_numbers.add(int(page_match.group(1)))
                
                # Visitar cada página (limitado a 10 para no sobrecargar)
                for page_num in sorted(page_numbers)[:10]:
                    page_url = f"{base_url}?page={page_num}"
                    print(f"Extrayendo página {page_num}")
                    page_html = self.get_page_with_requests(page_url) or self.get_page_with_selenium(page_url)
                    if page_html:
                        page_professionals = self.extract_professionals_info(page_html)
                        professionals_list.extend(page_professionals)
                        print(f"Se encontraron {len(page_professionals)} profesionales en la página {page_num}")
                    time.sleep(random.uniform(2, 4))
                break
    
    def save_to_json(self, data, filename='prevencionistas_chile.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Datos guardados en {filename}")
    
    def save_to_csv(self, data, filename='prevencionistas_chile.csv'):
        if not data:
            print("No hay datos para guardar")
            return
            
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Datos guardados en {filename}")
    
    def run(self):
        print("Iniciando extracción de datos de prevencionistas en Chile...")
        professionals = self.search_directory()
        
        if professionals:
            print(f"Se extrajeron {len(professionals)} profesionales")
            self.save_to_json(professionals)
            self.save_to_csv(professionals)
            return professionals
        else:
            print("No se pudo extraer información")
            return []

if __name__ == "__main__":
    scraper = ChilePrevencionScraper()
    data = scraper.run()
