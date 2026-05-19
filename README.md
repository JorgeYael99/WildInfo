# WildInfo 🌿 — Enciclopedia Interactiva de Biodiversidad

WildInfo es una aplicación web educativa que permite explorar el reino animal, obtener información científica detallada, visualizar mapas de distribución geográfica y construir una colección personal de especies. Está diseñada como un proyecto escolar de biodiversidad con validación estricta de taxonomía (solo acepta términos del reino Animalia).

## Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Frontend      │────▶│   FastAPI API    │────▶│  PostgreSQL │
│ (HTML/CSS/JS)   │     │   (Python 3.12)  │     │             │
│  Nginx :80      │     │   :8000          │     │  :5432      │
└─────────────────┘     └───────┬──────────┘     └─────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              API Ninjas   Unsplash   Wikipedia/GBIF
              (taxonomía)  (imágenes)  (resúmenes)
```

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Backend | Python 3.12 + FastAPI + Uvicorn |
| Frontend | HTML5, CSS3, JavaScript vanilla |
| Base de datos | PostgreSQL 15 (vía asyncpg) |
| Contenerización | Docker + docker-compose |
| Servidor web frontend | Nginx (Alpine) |
| APIs externas | API Ninjas (Animales), Unsplash (Imágenes), Wikipedia (Resúmenes), GBIF (Mapas de calor) |

## Estructura del proyecto

```
WildInfo/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── core/
│   │   └── config.py        # Configuración desde .env (Pydantic Settings)
│   ├── models/
│   │   └── database.py      # Conexión a PostgreSQL y creación de tablas
│   ├── routes/
│   │   ├── auth.py          # Registro, login, logout
│   │   ├── animales.py      # CRUD de animales, búsqueda, Wikipedia, mapa de calor
│   │   └── perfil.py        # Perfil de usuario, puntos, rangos, badges
│   ├── services/
│   │   ├── api_ninjas.py    # Traducción ES→EN + consulta API Ninjas
│   │   ├── unsplash.py      # Búsqueda de imágenes
│   │   └── wikipedia.py     # Resúmenes desde Wikipedia ES
│   └── tests/
│       └── test_services.py # Tests asíncronos con pytest
├── frontend/
│   ├── index.html           # Landing page
│   ├── login.html           # Inicio de sesión
│   ├── registro.html        # Registro de usuarios
│   ├── panel.html           # Panel principal (buscador, mapa, quiz)
│   ├── perfil.html          # Perfil y configuración de cuenta
│   ├── css/styles.css       # Estilos (tema naturaleza claro)
│   └── js/app.js            # Lógica del frontend
├── docker/
│   └── Dockerfile           # Dockerfile del backend (con PYTHONPATH)
├── frontend/Dockerfile      # Dockerfile del frontend (Nginx)
├── Dockerfile               # Dockerfile alternativo (raíz)
├── docker-compose.yml       # Orquestación (API + DB + Frontend)
├── requirements.txt         # Dependencias Python
├── .env                     # Variables de entorno (NO versionar)
├── .env.example             # Template para .env
├── .dockerignore
├── .gitignore
└── TESTING_CHECKLIST.md     # Guía de pruebas
```

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
- Rutas protegidas con API Key (X-API-KEY)
- Contraseñas hasheadas con bcrypt
- Validación estricta de reino Animalia

## Requisitos previos

- [Docker](https://docs.docker.com/desktop/) y [Docker Compose](https://docs.docker.com/compose/install/)
- Claves de API gratuitas (ver sección siguiente)

## Claves de API necesarias

| Servicio | Variable en .env | Cómo obtenerla |
|----------|-----------------|----------------|
| [API Ninjas](https://api-ninjas.com/) | `API_NINJS_KEY` | Registrarse en api-ninjas.com, plan gratuito: 50,000 requests/mes |
| [Unsplash](https://unsplash.com/developers) | `UNSPLASH_ACCESS_KEY` | Crear app en unsplash.com/developers, Access Key gratuita |

> **Nota:** El archivo `.env` incluido en el repositorio contiene claves de ejemplo. **No uses estas claves en producción.** Regístrate para obtener tus propias claves.

## Inicialización rápida (con Docker)

```powershell
# 1. Clonar y entrar al proyecto
git clone <repo-url> WildInfo
cd WildInfo

# 2. Configurar variables de entorno
#    Edita .env con tus propias claves de API
#    (opcional) Cambia POSTGRES_PASSWORD y API_SECRET_KEY

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

## Inicialización manual (sin Docker)

### Backend

```powershell
# 1. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env (ajusta DATABASE_URL para conexión local)
#    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# 4. Asegúrate de tener PostgreSQL corriendo en localhost:5432

# 5. Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
# Opción A: Servir con Python (puerto 3000)
python -m http.server 3000 --directory frontend

# Opción B: Servir con cualquier otro servidor estático
#    El frontend apunta a http://localhost:8000 para la API
```

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

> 🔒 = Requiere headers: `Authorization: Bearer <token>`, `X-User-Id: <id>`, `X-Username: <username>`, `X-API-KEY: <clave>`

## Variables de entorno (`.env`)

```env
# Servidor
PORT=8000
HOST=0.0.0.0

# APIs Externas
API_NINJS_KEY=tu_clave_aqui
UNSPLASH_ACCESS_KEY=tu_clave_aqui

# Base de datos
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres

# CORS
ORIGEN_PERMITIDO=http://127.0.0.1:3000

# API Key para rutas protegidas
API_SECRET_KEY=Cisco_Net_2026_ClaveSegura
```

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

## Ejecutar tests

```powershell
# Con Docker
docker exec -it wildinfo-api pytest app/tests/ -v

# Sin Docker
pytest app/tests/ -v
```

## Notas importantes

- **Validación de Reino:** WildInfo solo acepta animales del reino Animalia. Si buscas un término que no sea animal (plantas, hongos, etc.), la API devuelve un error 400.
- **Traducción automática:** Si buscas en español, el backend traduce automáticamente a inglés para consultar API Ninjas, y luego devuelve los resultados en el idioma original del animal.
- **Base de datos:** Las tablas se crean automáticamente al iniciar la API (usuarios, perfil_usuario, animales_guardados).
- **Persistencia:** Los datos de PostgreSQL persisten gracias al volumen `postgres_data` definido en docker-compose.yml.
- **CORS:** El backend permite orígenes específicos configurados en `app/main.py`. En producción, ajusta `ORIGEN_PERMITIDO` en `.env`.

## Licencia

Proyecto educativo — uso libre para fines académicos.
