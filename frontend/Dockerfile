# Usamos una imagen oficial y muy ligera de Nginx
FROM nginx:alpine

# Copiamos todos los archivos estáticos (HTML, CSS, JS) de tu carpeta frontend
# al directorio desde donde Nginx sirve las páginas web
COPY . /usr/share/nginx/html

# Nginx usa por defecto el puerto 80, así que lo exponemos
EXPOSE 80