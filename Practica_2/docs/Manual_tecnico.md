# Manual técnico — SmartBot Hospital

## 1. Información general

**SmartBot Hospital** es un sistema de atención automatizada desarrollado para el Hospital Vida Central. Permite responder consultas administrativas mediante Telegram y administrar el conocimiento desde una aplicación web.

El sistema fue desarrollado como parte de la Práctica 2 del curso Inteligencia Artificial 1.

### Información académica

* **Estudiante:** Nelson Emanuel Cún Bálan
* **Carné:** 201222010
* **Curso:** Inteligencia Artificial 1
* **Universidad:** Universidad de San Carlos de Guatemala
* **Facultad:** Facultad de Ingeniería

---

## 2. Objetivo del sistema

El objetivo principal es proporcionar un mecanismo automatizado para responder preguntas frecuentes relacionadas con servicios administrativos hospitalarios.

El sistema permite:

* Recibir preguntas desde Telegram.
* Buscar respuestas almacenadas en PostgreSQL.
* Resolver coincidencias exactas y aproximadas.
* Registrar cada consulta recibida.
* Administrar categorías, preguntas y respuestas.
* Consultar estadísticas de uso.
* Configurar el chat utilizado por Telegram.
* Ejecutar todos los componentes mediante Docker Compose.

---

## 3. Alcance

SmartBot Hospital responde consultas administrativas como:

* Horarios de atención.
* Horarios de visitas.
* Solicitud de citas.
* Documentos requeridos.
* Métodos de pago.
* Seguros médicos.
* Resultados de laboratorio.
* Servicios disponibles.
* Instalaciones hospitalarias.

El sistema no realiza diagnósticos médicos ni recomienda tratamientos.

---

## 4. Tecnologías utilizadas

| Componente             | Tecnología          |
| ---------------------- | ------------------- |
| Lenguaje del backend   | Python 3.12         |
| Framework del backend  | FastAPI             |
| Servidor ASGI          | Uvicorn             |
| ORM                    | SQLAlchemy          |
| Validación de datos    | Pydantic            |
| Base de datos          | PostgreSQL 16       |
| Controlador PostgreSQL | Psycopg             |
| Autenticación          | JSON Web Token      |
| Frontend               | React 18            |
| Herramienta frontend   | Vite                |
| Bot                    | python-telegram-bot |
| Contenedores           | Docker              |
| Orquestación local     | Docker Compose      |
| Control de versiones   | Git y GitHub        |

---

## 5. Arquitectura del sistema

![Diagrama de arquitectura](./diagramas/Diagrama_arquitectura.png)

---

## 6. Capas de la aplicación

### 6.1 Capa de presentación

Está formada por:

* Panel administrativo React.
* Bot de Telegram.

El panel permite administrar la información del sistema.

El bot recibe preguntas y muestra las respuestas obtenidas desde la API.

### 6.2 Capa de API

Está implementada mediante rutas de FastAPI.

Sus responsabilidades principales son:

* Recibir solicitudes HTTP.
* Validar datos de entrada.
* Verificar autenticación.
* Ejecutar servicios de aplicación.
* Devolver respuestas JSON.

### 6.3 Capa de servicios

Contiene las reglas de negocio.

Entre sus responsabilidades se encuentran:

* Autenticación.
* Normalización de preguntas.
* Búsqueda exacta.
* Búsqueda aproximada.
* Registro de consultas.
* Envío de mensajes a Telegram.
* Generación de estadísticas.

### 6.4 Capa de repositorios

Encapsula el acceso a PostgreSQL.

Cada repositorio se encarga de consultar o modificar una entidad específica.

Esto evita que las rutas y servicios ejecuten directamente operaciones sobre la base de datos.

### 6.5 Capa de persistencia

Está compuesta por:

* Modelos SQLAlchemy.
* Sesiones de base de datos.
* PostgreSQL.
* Scripts SQL de inicialización.

---

## 7. Estructura del proyecto

```text
Practica_2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
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
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── telegram-bot/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 8. Componentes del sistema

### 8.1 Backend

El backend se ejecuta en el contenedor:

```text
smartbot-backend
```

Puerto expuesto:

```text
8000
```

Funciones principales:

* Autenticación administrativa.
* CRUD de categorías.
* CRUD de preguntas.
* CRUD de respuestas.
* Resolución de consultas.
* Configuración del bot.
* Historial.
* Estadísticas.
* Mensajes de prueba a Telegram.

### 8.2 Frontend

El frontend se ejecuta en:

```text
smartbot-frontend
```

Puerto:

```text
5173
```

Secciones disponibles:

* Inicio de sesión.
* Resumen.
* Categorías.
* Preguntas y respuestas.
* Historial.
* Configuración.

### 8.3 Bot de Telegram

El bot se ejecuta en:

```text
smartbot-telegram
```

Utiliza long polling para recibir actualizaciones desde Telegram.

Comandos disponibles:

```text
/start
/help
/chatid
```

Los mensajes normales se envían al backend mediante:

```text
POST /api/v1/queries/resolve
```

### 8.4 PostgreSQL

La base de datos se ejecuta en:

```text
smartbot-db
```

La información se conserva en el volumen:

```text
smartbot_postgres_data
```

---

## 9. Modelo de datos

El sistema utiliza seis tablas principales.

![Diagrama de entidad-relación](./diagramas/Diagrama%20ER.png)

### 9.1 admin_users

Almacena los usuarios administrativos.

Campos principales:

* `id`
* `username`
* `password_hash`
* `full_name`
* `is_active`
* `created_at`
* `updated_at`

El nombre de usuario es único.

La contraseña se almacena mediante hash y no como texto plano.

### 9.2 categories

Almacena las categorías utilizadas para organizar las preguntas.

Campos principales:

* `id`
* `name`
* `description`
* `is_active`
* `created_at`
* `updated_at`

### 9.3 questions

Almacena las preguntas frecuentes.

Campos principales:

* `id`
* `category_id`
* `question_text`
* `normalized_text`
* `is_active`
* `created_at`
* `updated_at`

Cada pregunta pertenece a una categoría.

### 9.4 answers

Almacena las respuestas asociadas a las preguntas.

Campos principales:

* `id`
* `question_id`
* `answer_text`
* `is_active`
* `created_at`
* `updated_at`

Cada pregunta puede tener una respuesta asociada.

### 9.5 bot_settings

Almacena la configuración general del bot.

Campos principales:

* `id`
* `hospital_name`
* `telegram_chat_id`
* `bot_username`
* `welcome_message`
* `unknown_question_message`
* `is_active`
* `created_at`
* `updated_at`

La aplicación utiliza un único registro de configuración.

### 9.6 query_logs

Registra las consultas procesadas.

Campos principales:

* `id`
* `telegram_user_id`
* `telegram_username`
* `telegram_first_name`
* `telegram_chat_id`
* `original_query`
* `normalized_query`
* `question_id`
* `category_id`
* `response_text`
* `was_answered`
* `created_at`

---

## 10. Relaciones de la base de datos

Las relaciones principales son:

```text
categories 1 ---- N questions
questions  1 ---- 0..1 answers
questions  1 ---- N query_logs
categories 1 ---- N query_logs
```

Una categoría puede contener varias preguntas.

Cada pregunta puede tener una respuesta.

Un registro del historial puede quedar asociado con la pregunta y categoría encontradas.

---

## 11. Scripts de inicialización

La carpeta:

```text
database/init/
```

contiene los scripts ejecutados automáticamente por PostgreSQL cuando se crea el volumen por primera vez.

### 11.1 01_schema.sql

Crea:

* Extensiones necesarias.
* Tablas.
* Claves primarias.
* Claves foráneas.
* Índices.
* Restricciones.
* Triggers de actualización.

### 11.2 02_initial_data.sql

Registra:

* Usuario administrador.
* Contraseña administrativa cifrada.
* Configuración inicial del hospital.
* Mensajes predeterminados.

### 11.3 03_faq_seed.sql

Registra:

* 5 categorías.
* 20 preguntas frecuentes.
* 20 respuestas.

El script utiliza operaciones idempotentes para evitar duplicados.

---

## 12. Datos iniciales

### Usuario administrativo

```text
Usuario: IA1-User
Contraseña: IA1-password@_new
```

### Institución

```text
Hospital Vida Central
```

### Catálogo inicial

```text
5 categorías
20 preguntas
20 respuestas
```

Las categorías iniciales son:

1. Horarios y visitas.
2. Citas y admisiones.
3. Pagos y seguros.
4. Documentos y resultados.
5. Servicios e instalaciones.

---

## 13. Variables de entorno

El archivo `.env.example` contiene las variables requeridas.

```env
POSTGRES_DB=smartbot
POSTGRES_USER=smartbot_user
POSTGRES_PASSWORD=replace_with_secure_password

DATABASE_URL=postgresql+psycopg://smartbot_user:replace_with_secure_password@db:5432/smartbot

JWT_SECRET_KEY=replace_with_secure_random_value
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:5173

BACKEND_URL=http://backend:8000/api/v1

TELEGRAM_BOT_TOKEN=
```

### Descripción

| Variable                      | Descripción                                 |
| ----------------------------- | ------------------------------------------- |
| `POSTGRES_DB`                 | Nombre de la base de datos                  |
| `POSTGRES_USER`               | Usuario de PostgreSQL                       |
| `POSTGRES_PASSWORD`           | Contraseña de PostgreSQL                    |
| `DATABASE_URL`                | Cadena de conexión utilizada por SQLAlchemy |
| `JWT_SECRET_KEY`              | Clave utilizada para firmar los tokens      |
| `JWT_ALGORITHM`               | Algoritmo JWT                               |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token                          |
| `CORS_ORIGINS`                | Orígenes permitidos por el backend          |
| `BACKEND_URL`                 | Dirección interna utilizada por el bot      |
| `TELEGRAM_BOT_TOKEN`          | Token generado mediante BotFather           |

El archivo `.env` no debe subirse al repositorio.

---

## 14. Instalación

### 14.1 Clonar el repositorio

```bash
git clone git@github.com:NelsonCun/-IA1-_VACASJUN2026_NelsonCun_201222010.git
```

Ingresar al proyecto:

```bash
cd -IA1-_VACASJUN2026_NelsonCun_201222010/Practica_2
```

### 14.2 Crear variables de entorno

```bash
cp .env.example .env
```

Editar:

```bash
nano .env
```

Generar una clave JWT:

```bash
openssl rand -hex 32
```

### 14.3 Construir servicios

```bash
docker compose up --build -d
```

### 14.4 Comprobar estado

```bash
docker compose ps
```

Los cuatro contenedores deben aparecer activos.

---

## 15. Direcciones del sistema

| Servicio             | Dirección                             |
| -------------------- | ------------------------------------- |
| Panel administrativo | `http://localhost:5173`               |
| API REST             | `http://localhost:8000`               |
| Swagger              | `http://localhost:8000/docs`          |
| ReDoc                | `http://localhost:8000/redoc`         |
| Health check         | `http://localhost:8000/api/v1/health` |

---

## 16. Funcionamiento de la autenticación

El flujo de autenticación es el siguiente:

1. El administrador introduce usuario y contraseña.
2. El frontend envía la solicitud al backend.
3. El backend consulta el usuario en PostgreSQL.
4. Se verifica la contraseña almacenada mediante hash.
5. El backend genera un token JWT.
6. El frontend almacena el token en `localStorage`.
7. Las solicitudes protegidas incluyen:

```http
Authorization: Bearer <token>
```

8. Cuando el token es inválido o expira, el usuario debe iniciar sesión nuevamente.

---

## 17. Resolución de consultas

Cuando el bot recibe una pregunta se ejecuta el siguiente proceso.

### 17.1 Normalización

La consulta se transforma para facilitar la comparación.

Se realizan estas operaciones:

* Conversión a minúsculas.
* Eliminación de tildes.
* Eliminación de signos de puntuación.
* Eliminación de espacios adicionales.

Ejemplo:

```text
¿Cuál es el horario de visitas?
```

se convierte en:

```text
cual es el horario de visitas
```

### 17.2 Coincidencia exacta

El sistema busca una pregunta cuyo texto normalizado sea igual al texto recibido.

Cuando existe coincidencia, la respuesta se devuelve con confianza `1.0`.

### 17.3 Coincidencia aproximada

Cuando no existe coincidencia exacta, se comparan las preguntas activas utilizando:

* `SequenceMatcher`.
* Coincidencia de palabras.
* Cobertura de palabras compartidas.

El umbral mínimo de aceptación es:

```text
0.68
```

Una consulta con puntuación inferior se considera desconocida.

### 17.4 Consulta desconocida

Cuando no se encuentra una coincidencia válida, se devuelve el mensaje almacenado en:

```text
bot_settings.unknown_question_message
```

La interacción se registra con:

```text
was_answered = false
```

### 17.5 Registro

Todas las consultas se almacenan en `query_logs`, hayan sido respondidas o no.

---

## 18. Comunicación con Telegram

El bot obtiene actualizaciones mediante long polling.

Flujo:

```text
Telegram
   |
   v
telegram-bot
   |
   v
POST /api/v1/queries/resolve
   |
   v
FastAPI
   |
   v
PostgreSQL
```

La respuesta JSON de la API contiene:

* Texto de respuesta.
* Indicador de coincidencia.
* Pregunta encontrada.
* Categoría encontrada.
* Nivel de confianza.

El bot toma el campo de respuesta y lo envía al usuario.

---

## 19. API REST

La API utiliza el prefijo:

```text
/api/v1
```

### Autenticación

| Método | Ruta          | Descripción                 |
| ------ | ------------- | --------------------------- |
| POST   | `/auth/login` | Iniciar sesión              |
| GET    | `/auth/me`    | Obtener usuario autenticado |

### Categorías

| Método | Ruta               | Descripción          |
| ------ | ------------------ | -------------------- |
| GET    | `/categories`      | Listar categorías    |
| POST   | `/categories`      | Crear categoría      |
| GET    | `/categories/{id}` | Consultar categoría  |
| PUT    | `/categories/{id}` | Actualizar categoría |
| DELETE | `/categories/{id}` | Eliminar categoría   |

### Preguntas

| Método | Ruta              | Descripción         |
| ------ | ----------------- | ------------------- |
| GET    | `/questions`      | Listar preguntas    |
| POST   | `/questions`      | Crear pregunta      |
| GET    | `/questions/{id}` | Consultar pregunta  |
| PUT    | `/questions/{id}` | Actualizar pregunta |
| DELETE | `/questions/{id}` | Eliminar pregunta   |

### Respuestas

| Método | Ruta            | Descripción          |
| ------ | --------------- | -------------------- |
| GET    | `/answers`      | Listar respuestas    |
| POST   | `/answers`      | Crear respuesta      |
| GET    | `/answers/{id}` | Consultar respuesta  |
| PUT    | `/answers/{id}` | Actualizar respuesta |
| DELETE | `/answers/{id}` | Eliminar respuesta   |

### Consultas

| Método | Ruta               | Descripción           |
| ------ | ------------------ | --------------------- |
| POST   | `/queries/resolve` | Resolver una consulta |

### Configuración

| Método | Ruta                              | Descripción                   |
| ------ | --------------------------------- | ----------------------------- |
| GET    | `/settings/telegram`              | Obtener configuración         |
| PUT    | `/settings/telegram`              | Actualizar configuración      |
| POST   | `/settings/telegram/test-message` | Enviar mensaje de prueba      |
| GET    | `/bot/config`                     | Obtener configuración pública |

### Historial

| Método | Ruta               | Descripción        |
| ------ | ------------------ | ------------------ |
| GET    | `/query-logs`      | Listar consultas   |
| GET    | `/query-logs/{id}` | Consultar registro |

### Estadísticas

| Método | Ruta                        | Descripción              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/statistics/summary`       | Resumen general          |
| GET    | `/statistics/top-questions` | Preguntas más utilizadas |
| GET    | `/statistics/top-queries`   | Consultas más frecuentes |
| GET    | `/statistics/by-category`   | Consultas por categoría  |

---

## 20. Docker Compose

El archivo `docker-compose.yml` define cuatro servicios.

### db

* Imagen: `postgres:16-alpine`.
* Utiliza volumen persistente.
* Ejecuta health check.
* Inicializa scripts SQL.

### backend

* Construido desde `backend/Dockerfile`.
* Expone el puerto 8000.
* Espera que PostgreSQL esté saludable.

### frontend

* Construido desde `frontend/Dockerfile`.
* Expone el puerto 5173.
* Se comunica con el backend mediante HTTP.

### telegram-bot

* Construido desde `telegram-bot/Dockerfile`.
* No necesita publicar puertos.
* Se conecta con Telegram mediante Internet.
* Se comunica internamente con el backend.

---

## 21. Red y persistencia

Todos los servicios utilizan:

```text
smartbot-network
```

PostgreSQL conserva sus datos mediante:

```text
smartbot_postgres_data
```

Detener los contenedores no elimina la base de datos:

```bash
docker compose down
```

Eliminar el volumen sí borra todos los datos:

```bash
docker compose down -v
```

Este último comando debe utilizarse con precaución.

---

## 22. Requerimientos funcionales

| Código | Requerimiento                                        |
| ------ | ---------------------------------------------------- |
| RF-01  | El administrador debe poder iniciar sesión           |
| RF-02  | El sistema debe permitir gestionar categorías        |
| RF-03  | El sistema debe permitir gestionar preguntas         |
| RF-04  | El sistema debe permitir gestionar respuestas        |
| RF-05  | Cada pregunta debe pertenecer a una categoría        |
| RF-06  | El bot debe recibir mensajes desde Telegram          |
| RF-07  | El bot debe consultar la API REST                    |
| RF-08  | Las respuestas deben obtenerse desde PostgreSQL      |
| RF-09  | El sistema debe resolver coincidencias exactas       |
| RF-10  | El sistema debe resolver consultas aproximadas       |
| RF-11  | El sistema debe responder consultas desconocidas     |
| RF-12  | El sistema debe registrar el historial               |
| RF-13  | El panel debe mostrar estadísticas                   |
| RF-14  | El administrador debe configurar el chat de Telegram |
| RF-15  | El panel debe enviar mensajes de prueba              |
| RF-16  | El administrador debe activar o desactivar contenido |
| RF-17  | El administrador debe cerrar sesión                  |

---

## 23. Requerimientos no funcionales

| Código | Requerimiento                                          |
| ------ | ------------------------------------------------------ |
| RNF-01 | El backend debe estar desarrollado en Python           |
| RNF-02 | La comunicación debe realizarse mediante API REST      |
| RNF-03 | La base de datos debe ser PostgreSQL                   |
| RNF-04 | El sistema debe ejecutarse con Docker Compose          |
| RNF-05 | Los endpoints administrativos deben utilizar JWT       |
| RNF-06 | Los secretos deben almacenarse en variables de entorno |
| RNF-07 | El frontend debe ser adaptable                         |
| RNF-08 | La solución debe utilizar separación por capas         |
| RNF-09 | PostgreSQL debe incluir health check                   |
| RNF-10 | Los datos deben mantenerse mediante un volumen         |
| RNF-11 | El token de Telegram no debe aparecer en los registros |
| RNF-12 | Las respuestas no deben estar codificadas en el bot    |
| RNF-13 | Las relaciones deben mantener integridad referencial   |
| RNF-14 | El sistema debe manejar errores de comunicación        |

---

## 24. Verificación técnica

### Estado de contenedores

```bash
docker compose ps
```

### Estado del backend

```bash
curl http://localhost:8000/api/v1/health
```

### Estado del frontend

```bash
curl -I http://localhost:5173
```

### Compilación del frontend

```bash
docker compose exec frontend npm run build
```

### Validación de Python

```bash
docker compose exec backend python -m compileall -q app
```

### Registros del backend

```bash
docker compose logs --tail=100 backend
```

### Registros del bot

```bash
docker compose logs --tail=100 telegram-bot
```

---

## 25. Verificación de datos

Consultar cantidades:

```bash
docker compose exec db sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT
    (SELECT COUNT(*) FROM categories) AS categories,
    (SELECT COUNT(*) FROM questions) AS questions,
    (SELECT COUNT(*) FROM answers) AS answers,
    (SELECT COUNT(*) FROM query_logs) AS query_logs;
"'
```

Los valores iniciales esperados son:

```text
categories: 5
questions: 20
answers: 20
```

Comprobar preguntas sin respuesta:

```bash
docker compose exec db sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT q.id, q.question_text
FROM questions q
LEFT JOIN answers a
    ON a.question_id = q.id
WHERE a.id IS NULL;
"'
```

El resultado esperado es:

```text
0 rows
```

---

## 26. Prueba de autenticación

```bash
curl -X POST \
http://localhost:8000/api/v1/auth/login \
-H "Content-Type: application/json" \
-d '{
  "username": "IA1-User",
  "password": "IA1-password@_new"
}'
```

La respuesta debe contener:

```text
access_token
token_type
user
```

---

## 27. Prueba de resolución

### Consulta exacta

```bash
curl -X POST \
http://localhost:8000/api/v1/queries/resolve \
-H "Content-Type: application/json" \
-d '{
  "query": "¿Cuál es el horario de visitas?",
  "telegram_user_id": 9001,
  "telegram_username": "prueba",
  "telegram_first_name": "Prueba",
  "telegram_chat_id": 9001
}'
```

Debe devolver:

```text
matched: true
confidence: 1.0
```

### Consulta aproximada

```bash
curl -X POST \
http://localhost:8000/api/v1/queries/resolve \
-H "Content-Type: application/json" \
-d '{
  "query": "que tengo que llevar para mi cita",
  "telegram_user_id": 9001,
  "telegram_username": "prueba",
  "telegram_first_name": "Prueba",
  "telegram_chat_id": 9001
}'
```

Debe encontrar la pregunta relacionada con documentos requeridos.

### Consulta desconocida

```bash
curl -X POST \
http://localhost:8000/api/v1/queries/resolve \
-H "Content-Type: application/json" \
-d '{
  "query": "¿El hospital vende computadoras?",
  "telegram_user_id": 9001,
  "telegram_username": "prueba",
  "telegram_first_name": "Prueba",
  "telegram_chat_id": 9001
}'
```

Debe devolver:

```text
matched: false
```

---

## 28. Seguridad

Las medidas implementadas son:

* Contraseñas almacenadas mediante hash.
* Autenticación JWT.
* Rutas administrativas protegidas.
* Token de Telegram en `.env`.
* Archivo `.env` excluido mediante `.gitignore`.
* Validación de datos mediante Pydantic.
* Integridad referencial en PostgreSQL.
* Red interna de Docker.
* Reducción de registros HTTP sensibles.
* Separación de responsabilidades.
* El frontend no conoce la contraseña de PostgreSQL.
* El bot no contiene respuestas codificadas.

---

## 29. Manejo de errores

El sistema contempla:

* Credenciales inválidas.
* Token JWT inválido.
* Recursos inexistentes.
* Categorías duplicadas.
* Preguntas duplicadas.
* Respuestas duplicadas.
* Base de datos no disponible.
* Backend no disponible.
* Telegram no disponible.
* Chat ID no configurado.
* Bot desactivado.
* Consultas desconocidas.
* Datos de entrada inválidos.

---

## 30. Solución de problemas

### Los contenedores no inician

```bash
docker compose ps
docker compose logs
```

### PostgreSQL no está saludable

```bash
docker compose logs db
```

### El backend no responde

```bash
docker compose logs backend
curl http://localhost:8000/api/v1/health
```

### El frontend no abre

```bash
docker compose logs frontend
curl -I http://localhost:5173
```

### El bot no responde

```bash
docker compose logs telegram-bot
```

Verificar:

* Token correcto.
* Conexión a Internet.
* Backend activo.
* Bot iniciado mediante `/start`.
* Configuración activa.

### No aparecen los datos iniciales

Los scripts SQL solo se ejecutan cuando se crea el volumen.

Para reinicializar:

```bash
docker compose down -v
docker compose up --build -d
```

Este procedimiento elimina todos los datos almacenados.

---

## 31. Pruebas realizadas

Durante el desarrollo se verificó:

* Construcción de imágenes Docker.
* Inicio de los cuatro contenedores.
* Health check de PostgreSQL.
* Health check de FastAPI.
* Compilación del frontend.
* Login válido.
* Login inválido.
* Persistencia de sesión.
* Cierre de sesión.
* CRUD de categorías.
* CRUD de preguntas.
* CRUD de respuestas.
* Coincidencia exacta.
* Coincidencia aproximada.
* Consulta desconocida.
* Integración real con Telegram.
* Configuración del chat.
* Mensaje de prueba.
* Historial.
* Estadísticas.
* Persistencia en PostgreSQL.
* Protección de secretos.
* Verificación de que el token no se encuentre en Git.

---

## 32. Posibles mejoras

* Pruebas automatizadas de integración.
* Administración de múltiples usuarios.
* Recuperación de contraseña.
* Auditoría de cambios.
* Exportación del historial.
* Gráficas estadísticas.
* Webhooks de Telegram.
* Despliegue en un proveedor de nube.
* Certificado HTTPS.
* Búsqueda mediante extensiones especializadas de PostgreSQL.
* Configuración de múltiples hospitales.
* Respaldo automático de la base de datos.