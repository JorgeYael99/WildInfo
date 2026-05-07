# 1. Usar una imagen oficial de Python como base
FROM python:3.12-slim

# 2. Crear una carpeta de trabajo dentro de la "caja"
WORKDIR /app

# 3. Copiar la lista de librerías e instalarlas dentro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo tu código a la caja
COPY . .

# 5. Abrir el puerto 8000 para que el mundo lo vea
EXPOSE 8000

# 6. Comando para encender el servidor al iniciar la caja
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]