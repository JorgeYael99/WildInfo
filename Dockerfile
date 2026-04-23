# Usa una imagen oficial de Python ligera
FROM python:3.13-slim

# Cambiamos a /code para evitar conflictos con carpetas locales llamadas 'app'
WORKDIR /code

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Definir PYTHONPATH directamente en la imagen
ENV PYTHONPATH=/code