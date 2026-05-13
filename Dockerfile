# Imagen base oficial de Python (ligera)
FROM python:3.11-slim

# Metadatos de la imagen
LABEL maintainer="Proyecto MLOps - Diagnóstico Médico"
LABEL description="Servicio de predicción de estado de salud para médicos"
LABEL version="1.0"

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero el archivo de dependencias para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY app.py .
COPY templates/ ./templates/

# Exponer el puerto en el que corre Flask
EXPOSE 5000

# Variable de entorno para modo producción de Flask
ENV FLASK_ENV=production

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
