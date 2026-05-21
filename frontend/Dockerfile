FROM nginx:alpine

# Instalar gettext (proporciona envsubst)
RUN apk add --no-cache gettext

# Copiar archivos estáticos del frontend
COPY . /usr/share/nginx/html

# Copiar la plantilla de configuración (sin extensión .template en el destino final)
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Exponer puerto
EXPOSE 80

# El CMD por defecto de nginx:alpine procesa los archivos en /etc/nginx/templates/
# Pero para asegurar, forzamos la sustitución manual:
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]