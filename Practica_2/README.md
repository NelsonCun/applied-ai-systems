# SmartBot Hospital

Sistema de respuestas automatizadas mediante un bot de Telegram, una API
REST, PostgreSQL y un panel administrativo web.

## Tecnologías

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- React
- Vite
- Telegram Bot API
- Docker
- Docker Compose

## Arquitectura

La solución utiliza una arquitectura en capas:

- Presentación: panel administrativo y bot de Telegram.
- API: endpoints REST desarrollados con FastAPI.
- Aplicación: servicios responsables de los casos de uso.
- Persistencia: repositorios y modelos SQLAlchemy.
- Base de datos: PostgreSQL.

El bot de Telegram no consulta directamente PostgreSQL. Todas las consultas se realizan mediante la API REST.

## Configuración inicial

Crear el archivo de variables de entorno:

```bash
cp .env.example .env
```

Configurar valores seguros y agregar el token generado mediante BotFather.

## Ejecución

```bash
docker compose up --build -d
```

## Servicios
* Panel administrativo: http://localhost:5173
* API REST: http://localhost:8000
* Swagger: http://localhost:8000/docs
* Health check: http://localhost:8000/api/v1/health

## Detener servicios

```bash
docker compose down
```

No utilizar docker compose down -v salvo que se desee eliminar también todos los datos almacenados en PostgreSQL.