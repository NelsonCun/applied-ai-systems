# SmartBot Hospital

Sistema de atención automatizada para el **Hospital Vida Central**, desarrollado como parte de la Práctica 2 del curso Inteligencia Artificial 1.

## Información académica

* **Estudiante:** Nelson Emanuel Cún Bálan
* **Carné:** 201222010
* **Curso:** Inteligencia Artificial 1
* **Universidad:** Universidad de San Carlos de Guatemala
* **Facultad:** Facultad de Ingeniería

## Descripción

SmartBot Hospital es una plataforma que permite responder consultas administrativas mediante un bot de Telegram.

El sistema está compuesto por:

* Un panel administrativo desarrollado con React.
* Una API REST desarrollada con FastAPI.
* Una base de datos PostgreSQL.
* Un bot conectado con Telegram.
* Contenedores administrados con Docker Compose.

Las preguntas, respuestas, categorías, configuraciones e interacciones se almacenan en PostgreSQL. El bot no contiene respuestas escritas directamente en su código, sino que consulta la API REST para obtenerlas desde la base de datos.

## Funcionalidades

### Panel administrativo

* Inicio de sesión mediante usuario y contraseña.
* Autenticación con JSON Web Token.
* Gestión de categorías.
* Gestión de preguntas.
* Gestión de respuestas.
* Visualización del historial de consultas.
* Estadísticas de utilización.
* Configuración del bot.
* Configuración del ID del chat o grupo.
* Envío de mensajes de prueba a Telegram.
* Activación y desactivación del servicio de consultas.

### Bot de Telegram

* Recepción de mensajes mediante long polling.
* Consulta de respuestas a través de la API REST.
* Búsqueda exacta de preguntas.
* Búsqueda aproximada de preguntas similares.
* Manejo de consultas desconocidas.
* Registro de usuarios, chats y mensajes.
* Comandos `/start`, `/help` y `/chatid`.

### Base de datos

El sistema incluye inicialmente:

* 5 categorías.
* 20 preguntas frecuentes.
* 20 respuestas asociadas.
* 1 usuario administrador.
* Configuración inicial del Hospital Vida Central.

## Tecnologías utilizadas

| Componente           | Tecnología              |
| -------------------- | ----------------------- |
| Backend              | Python 3.12 y FastAPI   |
| ORM                  | SQLAlchemy              |
| Validaciones         | Pydantic                |
| Base de datos        | PostgreSQL 16           |
| Frontend             | React 18 y Vite         |
| Bot                  | python-telegram-bot     |
| Autenticación        | JWT                     |
| Contenedores         | Docker y Docker Compose |
| Control de versiones | Git y GitHub            |

## Arquitectura

El sistema utiliza una arquitectura en capas:

1. **Presentación**

   * Panel administrativo React.
   * Bot de Telegram.

2. **API**

   * Rutas REST desarrolladas con FastAPI.
   * Dependencias de autenticación y base de datos.

3. **Aplicación**

   * Servicios responsables de los casos de uso.
   * Validaciones y reglas de negocio.

4. **Persistencia**

   * Repositorios encargados de consultar y modificar información.

5. **Datos**

   * Modelos SQLAlchemy.
   * Base de datos PostgreSQL.

El frontend y el bot no acceden directamente a PostgreSQL. Toda operación se realiza mediante la API REST.

## Requisitos

Para ejecutar el proyecto se necesita:

* Git.
* Docker Engine o Docker Desktop.
* Docker Compose.
* Conexión a Internet para utilizar Telegram.
* Una cuenta de Telegram.
* Un bot creado mediante `@BotFather`.

No es necesario instalar Python, Node.js o PostgreSQL directamente cuando se utiliza Docker.

## Configuración inicial

Ubicarse dentro de la carpeta de la práctica:

```bash
cd Practica_2
```

Crear el archivo local de variables de entorno:

```bash
cp .env.example .env
```

Editar el archivo:

```bash
nano .env
```

Ejemplo de configuración:

```env
POSTGRES_DB=smartbot
POSTGRES_USER=smartbot_user
POSTGRES_PASSWORD=colocar_una_contrasena_segura

DATABASE_URL=postgresql+psycopg://smartbot_user:colocar_una_contrasena_segura@db:5432/smartbot

JWT_SECRET_KEY=colocar_un_valor_aleatorio_seguro
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:5173

BACKEND_URL=http://backend:8000/api/v1

TELEGRAM_BOT_TOKEN=colocar_el_token_generado_por_botfather
```

Para generar una clave segura para JWT se puede utilizar:

```bash
openssl rand -hex 32
```

El archivo `.env` está excluido del repositorio y no debe subirse a GitHub.

## Ejecución

Construir e iniciar todos los servicios:

```bash
docker compose up --build -d
```

Verificar el estado:

```bash
docker compose ps
```

Los contenedores esperados son:

* `smartbot-db`
* `smartbot-backend`
* `smartbot-frontend`
* `smartbot-telegram`

## Direcciones del sistema

| Servicio             | Dirección                           |
| -------------------- | ----------------------------------- |
| Panel administrativo | http://localhost:5173               |
| API REST             | http://localhost:8000               |
| Swagger              | http://localhost:8000/docs          |
| ReDoc                | http://localhost:8000/redoc         |
| Health check         | http://localhost:8000/api/v1/health |

## Credenciales administrativas

```text
Usuario: IA1-User
Contraseña: IA1-password@_new
```

Estas credenciales permiten ingresar al panel administrativo.

## Configuración de Telegram

### Crear el bot

1. Abrir Telegram.
2. Buscar `@BotFather`.
3. Ejecutar `/newbot`.
4. Asignar un nombre al bot.
5. Asignar un nombre de usuario terminado en `bot`.
6. Copiar el token generado.
7. Guardar el token en `TELEGRAM_BOT_TOKEN` dentro de `.env`.

Nunca se debe incluir el token dentro del repositorio.

### Reiniciar el bot

Después de configurar el token:

```bash
docker compose up --build -d telegram-bot
```

Verificar sus registros:

```bash
docker compose logs --tail=50 telegram-bot
```

Debe aparecer un mensaje indicando que SmartBot inició mediante long polling.

### Obtener el chat ID

Abrir una conversación con el bot y ejecutar:

```text
/start
/chatid
```

El bot mostrará el identificador del chat.

Este valor se registra desde la sección **Configuración** del panel administrativo.

## Datos iniciales

PostgreSQL ejecuta automáticamente los siguientes archivos cuando se crea el volumen por primera vez:

```text
database/init/01_schema.sql
database/init/02_initial_data.sql
database/init/03_faq_seed.sql
```

### Contenido de los scripts

* `01_schema.sql`: crea tablas, claves, índices, relaciones y triggers.
* `02_initial_data.sql`: crea el usuario administrador y la configuración inicial.
* `03_faq_seed.sql`: registra categorías, preguntas y respuestas.

Los scripts de inicialización pertenecen a la configuración de PostgreSQL. Durante la ejecución normal, el backend obtiene la información directamente desde la base de datos.

## Prueba del sistema

### Verificar el backend

```bash
curl http://localhost:8000/api/v1/health
```

La respuesta debe indicar que la API está activa y PostgreSQL está conectado.

### Verificar el frontend

```bash
curl -I http://localhost:5173
```

Debe devolver un estado HTTP 200.

### Verificar el bot

```bash
docker compose logs --tail=50 telegram-bot
```

Después, desde Telegram, enviar una pregunta conocida:

```text
¿Cuál es el horario de visitas?
```

El bot debe responder utilizando la información almacenada en PostgreSQL.

También se puede enviar una consulta desconocida:

```text
¿El hospital vende computadoras?
```

El bot debe responder con el mensaje configurado para preguntas sin coincidencia.

## Comandos útiles

### Ver todos los registros

```bash
docker compose logs -f
```

### Ver registros del backend

```bash
docker compose logs -f backend
```

### Ver registros del frontend

```bash
docker compose logs -f frontend
```

### Ver registros del bot

```bash
docker compose logs -f telegram-bot
```

### Reconstruir un servicio

```bash
docker compose up --build -d backend
```

### Reiniciar todos los servicios

```bash
docker compose restart
```

### Detener los contenedores

```bash
docker compose down
```

Este comando conserva la información de PostgreSQL.

### Eliminar contenedores y base de datos

```bash
docker compose down -v
```

Este comando elimina el volumen y toda la información persistente. Debe utilizarse únicamente cuando se quiera reinicializar completamente la base de datos.

## Estructura general

```text
Practica_2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   ├── init/
│   │   ├── 01_schema.sql
│   │   ├── 02_initial_data.sql
│   │   └── 03_faq_seed.sql
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── Dockerfile
│   └── package.json
├── telegram-bot/
│   ├── app/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Seguridad

La solución incluye las siguientes medidas:

* Contraseñas almacenadas mediante hash.
* Autenticación administrativa con JWT.
* Endpoints administrativos protegidos.
* Token de Telegram almacenado en variables de entorno.
* Archivo `.env` excluido de Git.
* Validaciones mediante Pydantic.
* Restricciones de integridad en PostgreSQL.
* Supresión de registros HTTP que podrían exponer el token.
* Separación entre presentación, negocio y persistencia.

## Persistencia

La información se almacena en el volumen:

```text
smartbot_postgres_data
```

La información permanece disponible aunque los contenedores se reinicien o se reconstruyan.