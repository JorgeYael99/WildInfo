# Lista de Verificación: Testing de Servicios Web (Docker) - WildInfo

## Instrucciones Previas

### 1. Construir y levantar los contenedores
```powershell
# En la raíz del proyecto (WildInfo/)
docker-compose build
docker-compose up -d
```

### 2. Verificar que todo está corriendo
```powershell
docker ps
```
Debes ver 3 contenedores: `wildinfo-api`, `wildinfo-db`, `wildinfo-frontend`

---

## Fase 1: Smoke Testing (Prueba de Humo)

**Objetivo:** Verificar que los servicios están "vivos" y los contenedores no se detuvieron.

| Paso | Acción |
|------|--------|
| 1 | Ejecuta `docker ps` en tu terminal |
| 2 | Verifica que en la columna STATUS los 3 contenedores digan "Up" |
| 3 | Si alguno no aparece, usa `docker logs [nombre]` para ver el error |

**Resultado esperado:**
- [ ] `wildinfo-api` → STATUS: Up
- [ ] `wildinfo-db` → STATUS: Up (healthy)
- [ ] `wildinfo-frontend` → STATUS: Up

**Comandos útiles:**
```powershell
docker logs wildinfo-api       # Logs del backend
docker logs wildinfo-db        # Logs de PostgreSQL
docker logs wildinfo-frontend  # Logs de Nginx
```

---

## Fase 2: Connectivity Testing (Prueba de Red Interna)

**Objetivo:** Verificar que el Backend responde correctamente.

| Paso | Acción |
|------|--------|
| 1 | Abre el navegador en `http://localhost:8000` |
| 2 | Abre `http://localhost:8000/docs` para ver el Swagger |
| 3 | Haz una petición GET a `http://localhost:8000/animales/info/leon` |

**Resultado esperado:**
- [ ] `http://localhost:8000` → `{"status": "WildInfo API Online"}`
- [ ] `http://localhost:8000/docs` → Interfaz Swagger UI visible
- [ ] `http://localhost:8000/animales/info/leon` → JSON con datos del león

**Si falla:**
- Error 404: Verifica el mapeo de puertos en `docker-compose.yml`
- Error de conexión: Verifica que el contenedor `wildinfo-api` esté corriendo

---

## Fase 3: Integration Testing (Frontend ↔ Backend)

**Objetivo:** Comprobar que la interfaz se comunica con la API sin errores CORS.

| Paso | Acción |
|------|--------|
| 1 | Abre el navegador en `http://localhost` (puerto 80) |
| 2 | Abre la Consola de Desarrollador (F12) |
| 3 | Ve a la pestaña "Network" (Red) y "Console" |
| 4 | Recarga la página |
| 5 | Intenta registrar un usuario y luego iniciar sesión |
| 6 | Busca un animal (ej: "oso") |

**Resultado esperado:**
- [ ] En Console: NO hay mensajes rojos de tipo "CORS Error"
- [ ] En Network: Petición GET al backend con estado 200 OK
- [ ] Interfaz: La página de login/registro funciona correctamente
- [ ] Interfaz: Los datos del animal se renderizan en pantalla
- [ ] Interfaz: Puedes guardar animales en tu colección

**Si hay error CORS:**
- Verifica que `app/main.py` incluya `"http://localhost"` en `allow_origins`
- Verifica que el contenedor backend esté corriendo en puerto 8000

---

## Fase 4: Database Persistence Testing (Prueba de Persistencia)

**Objetivo:** Asegurar que los datos sobreviven al reiniciar contenedores.

| Paso | Acción |
|------|--------|
| 1 | Inicia sesión en la app |
| 2 | Busca y guarda al menos 2 animales en tu colección |
| 3 | Ejecuta `docker-compose down` (detiene y borra contenedores) |
| 4 | Ejecuta `docker-compose up -d` (levanta de nuevo) |
| 5 | Espera 15 segundos a que PostgreSQL inicie |
| 6 | Inicia sesión de nuevo y recarga la página |

**Resultado esperado:**
- [ ] Los animales guardados siguen apareciendo en tu colección
- [ ] Tu perfil (puntos, rango, badges) se mantiene
- [ ] NO se perdieron datos tras el reinicio

**Si los datos desaparecieron:**
- El volumen `postgres_data` no se está montando correctamente
- Verifica que `docker volume ls` muestre `wildinfo_postgres_data`

---

## Fase 5: Security Testing (API Key)

**Objetivo:** Validar que las rutas protegidas rechazan accesos sin la API Key.

### Prueba A: Guardar animal sin API Key
```powershell
# Con Postman, Insomnia o PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/animales/" -Method POST -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer token_1_test"
    "X-User-Id" = "1"
    "X-Username" = "test"
    # SIN X-API-KEY
} -Body '{"nombre":"test","reino":"test","clase":"test","familia":"test","url_imagen":"","en_peligro":false}'
```

### Prueba B: Actualizar perfil sin API Key
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/perfil/progreso" -Method PUT -Headers @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer token_1_test"
    "X-User-Id" = "1"
    "X-Username" = "test"
    # SIN X-API-KEY
} -Body '{"puntos":0,"racha_maxima":0,"badge_oro":false,"badge_diversidad":false,"rango_titulo":"test"}'
```

**Resultado esperado:**
- [ ] Prueba A: Respuesta `401 Unauthorized` o `403 Forbidden`
- [ ] Prueba B: Respuesta `401 Unauthorized` o `403 Forbidden`
- [ ] Si incluyes el header `X-API-KEY: Cisco_Net_2026_ClaveSegura`, la petición funciona

---

## Fase 6: Variables de Entorno

**Objetivo:** Verificar que las credenciales se cargan desde `.env` y no están hardcodeadas.

| Paso | Acción |
|------|--------|
| 1 | Ejecuta `docker exec -it wildinfo-api env` |
| 2 | Verifica que las variables del `.env` aparecen |
| 3 | Revisa que NO hay claves escritas directamente en el código Python |

**Variables que deben estar presentes:**
- [ ] `API_NINJS_KEY`
- [ ] `UNSPLASH_ACCESS_KEY`
- [ ] `DATABASE_URL`
- [ ] `API_SECRET_KEY`

**Verificación de código:**
```powershell
# Buscar claves hardcodeadas en el backend
Select-String -Path "app\**\*.py" -Pattern "Cisco_Net_2026|gwFTSXUU|51FeTP2H"
```
- [ ] NO debe haber resultados (las claves solo deben estar en `.env`)

---

## Tabla de Resultados Final

| Categoría | Punto de Verificación | Valor | Resultado |
|-----------|----------------------|-------|-----------|
| **Infraestructura** | Los contenedores (frontend, backend, db) inician y permanecen en ejecución (Up) sin reinicios constantes | 15% | ⬜ Pendiente |
| **Conectividad API** | El Backend responde con datos JSON correctos al ser consultado directamente (vía navegador o Postman) | 15% | ⬜ Pendiente |
| **Integración (CORS)** | El Frontend muestra los datos del Backend en el navegador sin errores de "Cross-Origin" en la consola (F12) | 25% | ⬜ Pendiente |
| **Persistencia** | Tras ejecutar `docker-compose down` y `up`, los datos guardados en PostgreSQL siguen presentes | 20% | ⬜ Pendiente |
| **Seguridad** | Las rutas protegidas rechazan peticiones que no incluyen la `x-api-key` correcta en los headers | 15% | ⬜ Pendiente |
| **Ambiente** | El proyecto utiliza archivos `.env` para la configuración sensible en lugar de valores fijos en el código | 10% | ⬜ Pendiente |
| | **TOTAL** | **100%** | |

---

## ¿Cómo saber si está listo para producción?

Si pasan todas las pruebas anteriores, realiza esta última verificación:

1. **Variables de Entorno:**
   ```powershell
   docker exec -it wildinfo-api env | Select-String "API_NINJS_KEY|UNSPLASH|DATABASE_URL|API_SECRET"
   ```

2. **Logs limpios:**
   ```powershell
   docker logs wildinfo-api 2>&1 | Select-String "ERROR|WARNING"
   ```

3. **Health check de PostgreSQL:**
   ```powershell
   docker inspect wildinfo-db --format='{{.State.Health.Status}}'
   ```
   Debe devolver: `healthy`

4. **CORS en producción:** Cambia `ORIGEN_PERMITIDO` en `.env` al dominio real del servidor.

---

## Comandos de Referencia Rápida

```powershell
# Construir y levantar
docker-compose build
docker-compose up -d

# Ver estado
docker ps
docker-compose ps

# Ver logs
docker logs wildinfo-api
docker logs wildinfo-db
docker logs wildinfo-frontend
docker-compose logs -f

# Detener todo
docker-compose down

# Detener y borrar volúmenes (CUIDADO: pierde datos)
docker-compose down -v

# Entrar al contenedor del backend
docker exec -it wildinfo-api bash

# Entrar a la base de datos
docker exec -it wildinfo-db psql -U postgres

# Reconstruir sin caché
docker-compose build --no-cache
```
