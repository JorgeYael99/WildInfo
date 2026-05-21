FROM nginx:alpine

# Instalar gettext (contiene envsubst)
RUN apk add --no-cache gettext

# Copiar archivos estáticos del frontend
COPY . /usr/share/nginx/html

# Copiar la plantilla de configuración (sin extensión .template ahora)
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# Exponer puerto
EXPOSE 80

# Al arrancar, reemplazar la variable y generar el archivo real
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]