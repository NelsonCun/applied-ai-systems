# Base de datos de SmartBot Hospital

La base de datos utiliza PostgreSQL 16.

## Scripts de inicialización

Los archivos ubicados en `database/init` se ejecutan automáticamente
en orden alfabético cuando PostgreSQL crea un volumen de datos vacío.

1. `01_schema.sql`
   - Crea las tablas.
   - Define llaves primarias y foráneas.
   - Agrega restricciones e índices.
   - Configura triggers para `updated_at`.

2. `02_initial_data.sql`
   - Registra el usuario administrador requerido.
   - Registra la configuración inicial del bot.

## Datos administrables

Las categorías, preguntas y respuestas no se incluyen en los scripts SQL.
Deben registrarse mediante la API REST o el panel administrativo para evitar
almacenarlas de forma estática en el código fuente.

## Ejecución inicial

```bash
docker compose up --build -d
```

## Reinicialización completa

Los scripts SQL solamente se vuelven a ejecutar si el volumen de PostgreSQL
está vacío.

```bash
docker compose down -v
docker compose up --build -d
```

El comando docker compose down -v elimina permanentemente todos los datos
almacenados. No debe utilizarse después de registrar información importante.