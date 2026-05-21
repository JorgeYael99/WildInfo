FROM nginx:alpine

# Instalar gettext (contiene envsubst)
RUN apk add --no-cache gettext

# Copiar archivos estáticos
COPY . /usr/share/nginx/html

# Copiar la plantilla de configuración
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Exponer puerto
EXPOSE 80

# Al arrancar, reemplazar variables y ejecutar nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]