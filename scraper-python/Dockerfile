# 1. Imagen base
FROM python:3.11-slim

# 2. Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Instalar Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    chmod +x chromedriver && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# 5. Establecer directorio de trabajo
WORKDIR /app

# 6. Copiar archivos de requisitos
COPY requirements.txt .

# 7. Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 8. Copiar el resto de la aplicación
COPY . .

# 9. Exponer el puerto
EXPOSE 5000

# 10. Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]
