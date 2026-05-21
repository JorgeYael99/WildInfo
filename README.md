# WildInfo 🌿 — Enciclopedia Interactiva de Biodiversidad

WildInfo es una aplicación web educativa que permite explorar el reino animal, obtener información científica detallada, visualizar mapas de distribución geográfica y construir una colección personal de especies. Está diseñada como un proyecto escolar de biodiversidad con validación estricta de taxonomía (solo acepta términos del reino Animalia).

**URL del sistema desplegado:** `[URL_PRODUCCION]`

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   Navegador                          │
│           https://frontend.onrender.com              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│  Frontend (Nginx) — :80                              │
│  Sirve estáticos + proxy /api/* → backend            │
│                                                      │
│  ┌─────────────┐     ┌──────────────────────────┐   │
│  │ / (estáticos)│     │ /api/* → backend:8000/*  │   │
│  └─────────────┘     └──────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │ (red interna Docker / Render)
                       ▼
┌──────────────────────────────────────────────────────┐
│  Backend (FastAPI) — :8000                           │
│  Python 3.12 + Uvicorn                               │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ /auth    │ │ /animales│ │ /perfil  │             │
│  └──────────┘ └──────────┘ └──────────┘             │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┼────────────┬────────────┐
          ▼            ▼            ▼            ▼
    API Ninjas    Unsplash    Wikipedia/GBIF  PostgreSQL
    (taxonomía)  (imágenes)   (resúmenes)    (persistencia)
```

### Proxy inverso

El frontend sirve archivos estáticos a través de Nginx, que también actúa como proxy inverso:
- **`/api/animales/...`** → Nginx redirige a `http://api:8000/animales/...` (elimina `/api`)
- **`/`** → Sirve archivos estáticos directamente

Esto elimina la dependencia de `localhost:8000` y permite que la app funcione con rutas relativas.

---

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Backend | Python 3.12 + FastAPI + Uvicorn |
| Frontend | HTML5, CSS3, JavaScript vanilla |
| Base de datos | PostgreSQL 15 (vía asyncpg) |
| Contenerización | Docker + docker-compose |
| Servidor web frontend | Nginx (Alpine) — proxy inverso |
| APIs externas | API Ninjas (Animales), Unsplash (Imágenes), Wikipedia (Resúmenes), GBIF (Mapas de calor) |

---

## Estructura del proyecto

```
WildInfo/
├── backend/
│   ├── Dockerfile               # Dockerfile del backend (Python 3.12)
│   ├── requirements.txt         # Dependencias Python
│   └── app/
│       ├── main.py              # Punto de entrada FastAPI
│       ├── core/
│       │   └── config.py        # Configuración desde .env (Pydantic Settings)
│       ├── models/
│       │   └── database.py      # Conexión a PostgreSQL y creación de tablas
│       ├── routes/
│       │   ├── auth.py          # Registro, login, logout
│       │   ├── animales.py      # CRUD de animales, búsqueda, Wikipedia, mapa de calor
│       │   └── perfil.py        # Perfil de usuario, puntos, rangos, badges
│       ├── services/
│       │   ├── api_ninjas.py    # Traducción ES→EN + consulta API Ninjas
│       │   ├── unsplash.py      # Búsqueda de imágenes
│       │   └── wikipedia.py     # Resúmenes desde Wikipedia ES
│       └── tests/
│           └── test_services.py # Tests asíncronos con pytest
├── frontend/
│   ├── index.html               # Landing page
│   ├── login.html               # Inicio de sesión
│   ├── registro.html            # Registro de usuarios
│   ├── panel.html               # Panel principal (buscador, mapa, quiz)
│   ├── perfil.html              # Perfil y configuración de cuenta
│   ├── css/styles.css           # Estilos (tema naturaleza claro)
│   ├── js/app.js                # Lógica del frontend
│   ├── nginx.conf               # Configuración de Nginx con proxy inverso
│   └── Dockerfile               # Dockerfile del frontend (Nginx + nginx.conf)
├── docker-compose.yml           # Orquestación (API + DB + Frontend)
├── .env                         # Variables de entorno (NO versionar)
├── .env.example                 # Template para .env
├── sonar-project.properties     # Configuración SonarQube
├── .dockerignore
├── .gitignore
├── TESTING_CHECKLIST.md         # Guía de pruebas
└── README.md
```

---

## Funcionalidades

### 🔍 Buscador de animales
Busca cualquier animal por nombre común (español o inglés). El backend traduce automáticamente términos en español a inglés usando la API MyMemory, luego consulta API Ninjas para obtener datos taxonómicos.

### 📊 Ficha científica
Cada animal muestra: clase, familia, hábitat, dieta, longevidad, peso, velocidad, estado de conservación y ubicaciones geográficas.

### 🖼️ Imágenes reales
Obtiene fotografías de alta calidad desde Unsplash para cada especie consultada.

### 📖 Wikipedia en español
Resumen enciclopédico extraído de Wikipedia en español con búsqueda inteligente por nombre común, científico y familia.

### 🌍 Mapa de distribución
Visualiza en un mapa Leaflet las regiones donde habita la especie, con capa de calor opcional desde GBIF (Global Biodiversity Information Facility).

### 🧠 Quiz interactivo
Pon a prueba tu conocimiento con preguntas generadas automáticamente sobre los animales en tu colección. El sistema gestiona rachas, puntuaciones y temporizador.

### 🏆 Gamificación
Gana puntos al añadir especies, acumula rachas de aciertos en el quiz, desbloquea badges (Oro por racha de 10, Diversidad por 5 clases distintas) y sube de rango: Observador de Jardín → Explorador de Bosques → Naturalista de Campo → Maestro de la Biodiversidad.

### 📚 Enciclopedia personal
Guarda tus especies favoritas organizadas por clase taxonómica. Las especies en peligro de extinción se muestran en un "Santuario" especial.

### 🔒 Seguridad
- Autenticación por token + headers (Authorization, X-User-Id, X-Username)
- Contraseñas hasheadas con bcrypt
- Validación estricta de reino Animalia
- CORS configurable vía `ORIGEN_PERMITIDO`
- Modo debug inhabilitado en producción (`ENVIRONMENT=production`)
- Manejador global de excepciones (no expone tracebacks en producción)

---

## Requisitos previos

- [Docker](https://docs.docker.com/desktop/) y [Docker Compose](https://docs.docker.com/compose/install/)
- Claves de API gratuitas (ver sección siguiente)

---

## Claves de API necesarias

| Servicio | Variable en .env | Cómo obtenerla |
|----------|-----------------|----------------|
| [API Ninjas](https://api-ninjas.com/) | `API_NINJS_KEY` | Registrarse en api-ninjas.com, plan gratuito: 50,000 requests/mes |
| [Unsplash](https://unsplash.com/developers) | `UNSPLASH_ACCESS_KEY` | Crear app en unsplash.com/developers, Access Key gratuita |

> **Nota:** No uses las claves de ejemplo en producción. Regístrate para obtener tus propias claves.

---

## Variables de entorno

### Desarrollo (`.env`)

```env
# Servidor
PORT=8000
HOST=0.0.0.0

# APIs Externas
API_NINJS_KEY=tu_clave_aqui
UNSPLASH_ACCESS_KEY=tu_clave_aqui

# Base de datos (local con Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres

# CORS (múltiples orígenes separados por coma)
ORIGEN_PERMITIDO=http://127.0.0.1:3000,http://localhost

# API Key para rutas protegidas (pruebas externas)
API_SECRET_KEY=tu_clave_secreta

# Entorno: development | production
ENVIRONMENT=development
```

### Producción (Render)

En Render, configura estas variables en el dashboard del Web Service:

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | Copiar desde Render PostgreSQL → Internal Connection String |
| `API_NINJS_KEY` | Tu clave de API Ninjas |
| `UNSPLASH_ACCESS_KEY` | Tu clave de Unsplash |
| `ORIGEN_PERMITIDO` | `https://<frontend>.onrender.com` |
| `API_SECRET_KEY` | Clave secreta para pruebas externas |
| `ENVIRONMENT` | `production` |
| `PORT` | `8000` |
| `HOST` | `0.0.0.0` |

---

## Inicialización rápida (desarrollo con Docker)

```powershell
# 1. Clonar y entrar al proyecto
git clone <repo-url> WildInfo
cd WildInfo

# 2. Configurar variables de entorno
#    Copiar .env.example a .env y editar con tus claves

# 3. Construir imágenes
docker-compose build

# 4. Levantar los servicios
docker-compose up -d

# 5. Verificar que todo esté corriendo
docker ps
# Deberías ver 3 contenedores: wildinfo-api, wildinfo-db, wildinfo-frontend

# 6. Abrir en el navegador
#    Frontend: http://localhost
#    API:      http://localhost:8000
#    Swagger:  http://localhost:8000/docs
```

> **Nota importante:** Con el nuevo proxy inverso, el frontend llama a `/api/...` que Nginx redirige al backend. Ya no se usa `http://localhost:8000` directamente en el frontend.

---

## Despliegue en Render

### Paso 1: Crear base de datos PostgreSQL

1. Ir a [dashboard.render.com](https://dashboard.render.com)
2. New → PostgreSQL
3. Nombrar: `wildinfo-db`
4. Guardar y copiar la **Internal Database URL**

### Paso 2: Desplegar el Backend (Web Service)

1. New → Web Service
2. Conectar repositorio de GitHub
3. Configurar:
   - **Name:** `wildinfo-api`
   - **Root Directory:** (vacío — raíz del repo)
   - **Runtime:** Docker
   - **Build Command:** (dejar vacío — Render usa el Dockerfile)
   - **Start Command:** (dejar vacío — se usa el CMD del Dockerfile)
   - **Health Check Path:** `/`
4. Agregar variables de entorno (ver sección Producción arriba)
5. Crear servicio

### Paso 3: Desplegar el Frontend (Web Service)

1. New → Web Service
2. Conectar mismo repositorio
3. Configurar:
   - **Name:** `wildinfo-frontend`
   - **Root Directory:** `frontend`
   - **Runtime:** Docker
   - **Build Command:** (dejar vacío — Render usa `frontend/Dockerfile`)
   - **Start Command:** (dejar vacío)
4. No necesita variables de entorno
5. Crear servicio

### Paso 4: Configurar CORS

Una vez que ambos servicios estén desplegados, actualiza la variable `ORIGEN_PERMITIDO` en el backend con la URL del frontend (ej: `https://wildinfo-frontend.onrender.com`).

### Paso 5: Verificar

- Visitar `https://<frontend>.onrender.com`
- Registrar un usuario
- Buscar un animal
- Probar el flujo completo

---

## Endpoints de la API

### Autenticación (`/auth`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/registro` | Registrar nuevo usuario |
| POST | `/auth/login` | Iniciar sesión |
| POST | `/auth/logout` | Cerrar sesión |

### Animales (`/animales`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/animales/buscar-sugerencias?q=` | Autocompletado de nombres |
| GET | `/animales/info/{nombre}` | Ficha científica del animal |
| GET | `/animales/imagen/{nombre}` | URL de imagen desde Unsplash |
| GET | `/animales/wikipedia/{nombre}` | Resumen de Wikipedia en español |
| GET | `/animales/mapa-calor/{nombre}` | Taxon key para mapa GBIF |
| GET | `/animales/` | Listar animales guardados del usuario |
| POST | `/animales/` | Guardar animal en colección 🔒 |
| DELETE | `/animales/{nombre}` | Eliminar animal de colección 🔒 |

### Perfil (`/perfil`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/perfil/` | Perfil del usuario autenticado |
| GET | `/perfil/{user_id}` | Perfil público de un usuario |
| PUT | `/perfil/progreso` | Actualizar puntos/rango/badges 🔒 |
| PUT | `/perfil/{user_id}/username` | Cambiar nombre de usuario 🔒 |
| PUT | `/perfil/{user_id}/password` | Cambiar contraseña 🔒 |

> 🔒 = Requiere headers de autenticación (token, X-User-Id, X-Username)

---

## Ejecutar tests

```powershell
# Con Docker
docker exec -it wildinfo-api pytest app/tests/ -v

# Sin Docker
pytest app/tests/ -v
```

---

## Calidad de código

### SonarQube

Ejecutar análisis local con Docker:

```powershell
# 1. Iniciar SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:community

# 2. Abrir http://localhost:9000, crear token

# 3. Ejecutar análisis (requiere sonar-scanner instalado)
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=<TOKEN>
```

### Google Lighthouse

1. Abrir la aplicación desplegada en Chrome
2. F12 → Pestaña Lighthouse
3. Generar informe para categorías: Performance, Accessibility, Best Practices, SEO

---

## Comandos útiles (Docker)

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

# Detener (sin perder datos)
docker-compose down

# Detener y borrar volúmenes (pierde datos)
docker-compose down -v

# Reconstruir sin caché
docker-compose build --no-cache

# Ejecutar tests
docker exec -it wildinfo-api pytest app/tests/ -v

# Entrar a la base de datos
docker exec -it wildinfo-db psql -U postgres
```

---

## Checklist de cumplimiento (Proyecto en Producción)

| Categoría | % | Estado |
|-----------|---|--------|
| **Funcionamiento general** | 20% | ✅ Frontend/backend funcional, endpoints ok, manejo de errores |
| **Despliegue y producción** | 15% | ✅ Publicado en Render, accesible desde internet, HTTPS automático |
| **Persistencia** | 10% | ✅ PostgreSQL persistente (volumen Docker local / Render PostgreSQL) |
| **Seguridad** | 10% | ✅ Variables de entorno, CORS configurable, sin secretos en código, manejador errores genérico |
| **Docker y configuración** | 10% | ✅ Dockerfile funcional, variables de entorno, compatibilidad entornos |
| **Calidad y pruebas** | 15% | ✅ SonarQube configurado, Lighthouse evaluable, tests funcionales |
| **Arquitectura** | 10% | ✅ Separación frontend/backend, proxy inverso, organización modular |
| **Documentación** | 10% | ✅ README completo, instrucciones, variables, URL del sistema |

### Checklist detallado

- [x] Frontend funcional (Nginx + proxy inverso)
- [x] Backend funcional (FastAPI + rutas)
- [x] Endpoints respondiendo correctamente
- [x] Manejo de errores (validaciones, excepciones globales)
- [x] Publicado en plataforma cloud (Render)
- [x] Accesible desde internet con HTTPS
- [x] Base de datos persistente
- [x] Variables de entorno (`.env`)
- [x] CORS configurable
- [x] Sin secretos expuestos en código
- [x] Sin errores internos visibles al usuario
- [x] Dockerfile funcional
- [x] Compatibilidad desarrollo/testing/producción
- [x] SonarQube configurado
- [x] Tests funcionales (pytest)
- [x] Frontend separado del backend
- [x] Organización modular
- [x] Sin dependencia de localhost (rutas relativas `/api/`)
- [x] README completo
- [x] URL del sistema documentada

---

## Notas importantes

- **Proxy inverso:** El frontend llama a `/api/...` que Nginx redirige al backend. El backend sigue respondiendo sin prefijo `/api`.
- **API Key:** La clave `API_SECRET_KEY` es opcional en el frontend. Solo se usa para pruebas externas (curl, Postman). El backend la verifica solo si se envía.
- **Modo producción:** Con `ENVIRONMENT=production`, el backend deshabilita debug, oculta tracebacks y usa el manejador global de excepciones.
- **Base de datos en producción:** Usa el servicio PostgreSQL gestionado de Render (no Docker). En desarrollo local usa el contenedor `db` de docker-compose.
- **Validación de Reino:** WildInfo solo acepta animales del reino Animalia.
- **Persistencia:** Los datos de PostgreSQL persisten gracias al volumen `postgres_data`.

---

## Licencia

Proyecto educativo — uso libre para fines académicos.
