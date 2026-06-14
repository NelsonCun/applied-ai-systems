# Requerimientos del sistema — SmartBot Hospital

## 1. Información general

**Sistema:** SmartBot Hospital

**Institución:** Hospital Vida Central

**Curso:** Inteligencia Artificial 1

**Estudiante:** Nelson Emanuel Cún Bálan

**Carné:** 201222010

SmartBot Hospital es un sistema de atención automatizada que responde consultas administrativas mediante Telegram y permite administrar el conocimiento desde una aplicación web.

---

## 2. Objetivo

Definir los requerimientos funcionales y no funcionales que debe cumplir SmartBot Hospital para garantizar su correcto funcionamiento, mantenimiento, seguridad y facilidad de uso.

---

## 3. Actores del sistema

### 3.1 Administrador

Persona encargada de gestionar el contenido y configuración del sistema.

Puede:

* Iniciar sesión.
* Gestionar categorías.
* Gestionar preguntas.
* Gestionar respuestas.
* Consultar historial.
* Consultar estadísticas.
* Configurar el bot.
* Enviar mensajes de prueba.
* Cerrar sesión.

### 3.2 Usuario de Telegram

Persona que realiza consultas administrativas mediante el bot.

Puede:

* Iniciar interacción con `/start`.
* Consultar ayuda mediante `/help`.
* Obtener el identificador del chat mediante `/chatid`.
* Enviar preguntas en lenguaje natural.
* Recibir respuestas conocidas.
* Recibir un mensaje cuando no existe una respuesta.

### 3.3 Telegram

Plataforma externa encargada de:

* Entregar mensajes al bot.
* Recibir mensajes enviados por SmartBot.
* Identificar usuarios y chats.

---

## 4. Requerimientos funcionales

### RF-01 — Inicio de sesión administrativo

El sistema debe permitir que un administrador inicie sesión mediante nombre de usuario y contraseña.

**Datos de entrada:**

* Nombre de usuario.
* Contraseña.

**Resultado esperado:**

* Si las credenciales son correctas, el sistema genera un token JWT.
* Si las credenciales son incorrectas, el acceso es rechazado.

**Prioridad:** Alta.

---

### RF-02 — Validación de sesión

El sistema debe validar el token JWT antes de permitir el acceso a las operaciones administrativas.

**Resultado esperado:**

* Un token válido permite continuar.
* Un token inválido o vencido obliga a iniciar sesión nuevamente.

**Prioridad:** Alta.

---

### RF-03 — Cierre de sesión

El administrador debe poder cerrar la sesión desde el panel administrativo.

**Resultado esperado:**

* El token almacenado en el navegador es eliminado.
* El usuario regresa a la pantalla de inicio de sesión.

**Prioridad:** Media.

---

### RF-04 — Crear categorías

El administrador debe poder registrar nuevas categorías.

**Datos requeridos:**

* Nombre.
* Descripción.
* Estado activo o inactivo.

**Validaciones:**

* El nombre no puede estar vacío.
* No deben existir categorías duplicadas.

**Prioridad:** Alta.

---

### RF-05 — Consultar categorías

El administrador debe poder visualizar las categorías registradas.

El sistema debe permitir:

* Buscar por nombre.
* Filtrar por estado.
* Consultar categorías activas e inactivas.

**Prioridad:** Alta.

---

### RF-06 — Actualizar categorías

El administrador debe poder modificar:

* Nombre.
* Descripción.
* Estado.

**Resultado esperado:**

Los cambios deben persistir en PostgreSQL.

**Prioridad:** Alta.

---

### RF-07 — Eliminar categorías

El administrador debe poder eliminar una categoría cuando no existan relaciones que comprometan la integridad de la información.

**Regla:**

Una categoría con preguntas asociadas no debe eliminarse de manera inconsistente.

**Prioridad:** Media.

---

### RF-08 — Crear preguntas

El administrador debe poder registrar preguntas frecuentes.

**Datos requeridos:**

* Categoría.
* Texto de la pregunta.
* Estado activo o inactivo.

**Resultado esperado:**

* La pregunta se almacena en PostgreSQL.
* El sistema genera su texto normalizado.

**Prioridad:** Alta.

---

### RF-09 — Consultar preguntas

El administrador debe poder visualizar las preguntas existentes.

El sistema debe permitir:

* Buscar por texto.
* Filtrar por categoría.
* Filtrar por estado.
* Visualizar si existe una respuesta asociada.

**Prioridad:** Alta.

---

### RF-10 — Actualizar preguntas

El administrador debe poder modificar:

* Categoría.
* Texto.
* Estado.

Cuando el texto cambie, el sistema debe actualizar su versión normalizada.

**Prioridad:** Alta.

---

### RF-11 — Eliminar preguntas

El administrador debe poder eliminar una pregunta.

**Resultado esperado:**

* La pregunta se elimina.
* La respuesta asociada también se elimina mediante la relación definida en PostgreSQL.

**Prioridad:** Media.

---

### RF-12 — Crear respuestas

El administrador debe poder registrar una respuesta para una pregunta.

**Datos requeridos:**

* Pregunta asociada.
* Texto de la respuesta.
* Estado activo o inactivo.

**Regla:**

Una pregunta solo puede tener una respuesta asociada.

**Prioridad:** Alta.

---

### RF-13 — Consultar respuestas

El administrador debe poder visualizar las respuestas relacionadas con las preguntas.

**Prioridad:** Alta.

---

### RF-14 — Actualizar respuestas

El administrador debe poder modificar:

* Texto.
* Estado.

Los cambios deben estar disponibles para futuras consultas de Telegram.

**Prioridad:** Alta.

---

### RF-15 — Eliminar respuestas

El administrador debe poder eliminar una respuesta sin eliminar la pregunta asociada.

**Resultado esperado:**

La pregunta permanece registrada, pero no podrá responder consultas hasta que tenga una respuesta activa.

**Prioridad:** Media.

---

### RF-16 — Recibir mensajes desde Telegram

El bot debe recibir mensajes enviados por usuarios mediante Telegram.

**Mecanismo:**

Long polling.

**Prioridad:** Alta.

---

### RF-17 — Comando de inicio

El bot debe responder al comando:

```text
/start
```

**Resultado esperado:**

Mostrar el mensaje de bienvenida configurado.

**Prioridad:** Media.

---

### RF-18 — Comando de ayuda

El bot debe responder al comando:

```text
/help
```

**Resultado esperado:**

Mostrar instrucciones básicas para utilizar SmartBot.

**Prioridad:** Media.

---

### RF-19 — Comando de identificación del chat

El bot debe responder al comando:

```text
/chatid
```

**Resultado esperado:**

Mostrar el identificador del chat actual.

**Prioridad:** Media.

---

### RF-20 — Resolver coincidencias exactas

El sistema debe buscar primero una pregunta cuyo texto normalizado coincida exactamente con la consulta recibida.

**Resultado esperado:**

* La respuesta se devuelve con confianza `1.0`.
* La interacción se registra como respondida.

**Prioridad:** Alta.

---

### RF-21 — Resolver coincidencias aproximadas

Cuando no exista coincidencia exacta, el sistema debe calcular la similitud con las preguntas activas.

**Criterios utilizados:**

* Similitud de secuencia.
* Palabras compartidas.
* Cobertura de palabras.

**Umbral mínimo:**

```text
0.68
```

**Resultado esperado:**

Cuando la puntuación alcanza el umbral, se devuelve la respuesta correspondiente.

**Prioridad:** Alta.

---

### RF-22 — Manejar consultas desconocidas

Cuando ninguna pregunta alcance el umbral de similitud, el sistema debe devolver el mensaje configurado para consultas desconocidas.

**Resultado esperado:**

* `matched` debe ser `false`.
* La consulta debe registrarse como no respondida.

**Prioridad:** Alta.

---

### RF-23 — Obtener respuestas desde PostgreSQL

Las respuestas enviadas por el bot deben obtenerse desde PostgreSQL mediante la API REST.

**Restricción:**

Las respuestas no deben estar codificadas directamente dentro del bot o del frontend.

**Prioridad:** Alta.

---

### RF-24 — Registrar historial de consultas

El sistema debe registrar cada consulta procesada.

**Datos almacenados:**

* Usuario de Telegram.
* Nombre.
* Chat.
* Consulta original.
* Consulta normalizada.
* Respuesta enviada.
* Pregunta encontrada.
* Categoría encontrada.
* Estado respondido o no respondido.
* Fecha y hora.

**Prioridad:** Alta.

---

### RF-25 — Consultar historial

El administrador debe poder visualizar el historial desde el panel.

El sistema debe permitir:

* Buscar registros.
* Filtrar por resultado.
* Navegar mediante paginación.

**Prioridad:** Media.

---

### RF-26 — Mostrar estadísticas generales

El panel debe mostrar:

* Consultas totales.
* Consultas respondidas.
* Consultas no respondidas.
* Tasa de respuesta.
* Usuarios únicos.
* Chats únicos.
* Categorías.
* Preguntas.
* Respuestas.

**Prioridad:** Media.

---

### RF-27 — Mostrar preguntas más utilizadas

El sistema debe mostrar las preguntas que han sido relacionadas con mayor cantidad de consultas.

**Prioridad:** Baja.

---

### RF-28 — Mostrar consultas frecuentes

El sistema debe mostrar los textos de consulta que se repiten con mayor frecuencia.

**Prioridad:** Baja.

---

### RF-29 — Mostrar estadísticas por categoría

El sistema debe calcular la cantidad de consultas relacionadas con cada categoría.

**Prioridad:** Baja.

---

### RF-30 — Consultar configuración del bot

El administrador debe poder visualizar:

* Nombre de la institución.
* Chat ID.
* Usuario del bot.
* Mensaje de bienvenida.
* Mensaje para consultas desconocidas.
* Estado del bot.

**Prioridad:** Alta.

---

### RF-31 — Actualizar configuración del bot

El administrador debe poder modificar la configuración disponible desde el panel.

**Resultado esperado:**

Los cambios deben almacenarse en PostgreSQL.

**Prioridad:** Alta.

---

### RF-32 — Configurar chat o grupo de Telegram

El administrador debe poder registrar el ID del chat o grupo utilizado para pruebas y notificaciones.

**Prioridad:** Alta.

---

### RF-33 — Activar o desactivar el bot

El administrador debe poder cambiar el estado general del bot.

**Resultado esperado:**

Cuando el bot esté desactivado, no debe procesar normalmente las consultas.

**Prioridad:** Media.

---

### RF-34 — Enviar mensaje de prueba

El panel debe permitir enviar un mensaje de prueba al chat configurado.

**Resultado esperado:**

* Telegram recibe el mensaje.
* El panel informa que la operación fue correcta.
* En caso de error, debe mostrarse una explicación.

**Prioridad:** Alta.

---

### RF-35 — Cargar datos iniciales

Al crear la base de datos por primera vez, el sistema debe registrar:

* Usuario administrador.
* Configuración inicial.
* Mínimo 3 categorías.
* Mínimo 20 preguntas.
* Mínimo 20 respuestas.

La implementación incluye:

* 5 categorías.
* 20 preguntas.
* 20 respuestas.

**Prioridad:** Alta.

---

### RF-36 — Verificar estado del sistema

La API debe proporcionar un endpoint de salud que indique:

* Estado de la API.
* Estado de conexión con PostgreSQL.

**Prioridad:** Media.

---

## 5. Requerimientos no funcionales

### RNF-01 — Lenguaje del backend

El backend debe estar desarrollado en Python.

**Cumplimiento:** Python 3.12.

---

### RNF-02 — Framework de API

La API debe utilizar un framework compatible con servicios REST.

**Cumplimiento:** FastAPI.

---

### RNF-03 — Base de datos

La información debe almacenarse en PostgreSQL.

**Cumplimiento:** PostgreSQL 16.

---

### RNF-04 — Comunicación REST

El frontend y el bot deben comunicarse con el backend mediante HTTP y JSON.

---

### RNF-05 — Separación por capas

La aplicación debe separar:

* Presentación.
* Rutas.
* Servicios.
* Repositorios.
* Modelos.
* Base de datos.

---

### RNF-06 — Contenedores

El sistema debe poder ejecutarse mediante Docker Compose.

Los servicios mínimos son:

* PostgreSQL.
* Backend.
* Frontend.
* Bot de Telegram.

---

### RNF-07 — Reproducibilidad

La aplicación debe poder ejecutarse en otro equipo utilizando:

```bash
docker compose up --build -d
```

sin instalar manualmente Python, Node.js o PostgreSQL.

---

### RNF-08 — Persistencia

La información debe conservarse mediante un volumen de Docker.

**Volumen:**

```text
smartbot_postgres_data
```

---

### RNF-09 — Seguridad de contraseñas

Las contraseñas administrativas no deben almacenarse como texto plano.

Deben utilizar una función de hash segura.

---

### RNF-10 — Autenticación

Los endpoints administrativos deben estar protegidos mediante JWT.

---

### RNF-11 — Protección de secretos

Los valores sensibles deben almacenarse en `.env`.

Incluye:

* Contraseña de PostgreSQL.
* Clave JWT.
* Token de Telegram.

---

### RNF-12 — Exclusión de secretos en Git

El archivo `.env` debe estar incluido en `.gitignore`.

---

### RNF-13 — Protección del token de Telegram

El token no debe:

* Guardarse en el código fuente.
* Subirse al repositorio.
* Mostrarse en el panel.
* Imprimirse en los registros normales.

---

### RNF-14 — Validación de datos

Los datos recibidos por la API deben validarse antes de procesarse.

**Cumplimiento:** Esquemas Pydantic.

---

### RNF-15 — Integridad referencial

PostgreSQL debe garantizar relaciones válidas mediante:

* Claves primarias.
* Claves foráneas.
* Restricciones únicas.
* Operaciones en cascada cuando correspondan.

---

### RNF-16 — Disponibilidad de PostgreSQL

El contenedor de PostgreSQL debe disponer de un health check.

El backend debe iniciar después de confirmar que la base está disponible.

---

### RNF-17 — Reinicio automático

Los servicios deben utilizar una política de reinicio que permita recuperarse ante fallos.

**Cumplimiento:**

```text
restart: unless-stopped
```

---

### RNF-18 — Diseño adaptable

La interfaz debe poder utilizarse en:

* Computadoras de escritorio.
* Computadoras portátiles.
* Tabletas.
* Teléfonos.

---

### RNF-19 — Usabilidad

La interfaz debe:

* Mostrar etiquetas claras.
* Utilizar mensajes comprensibles.
* Confirmar operaciones.
* Mostrar estados de carga.
* Mostrar errores.
* Evitar términos técnicos innecesarios para el usuario.

---

### RNF-20 — Rendimiento

Las operaciones normales del panel deben responder en un tiempo razonable dentro de una red local.

Las búsquedas deben utilizar índices y consultas optimizadas.

---

### RNF-21 — Trazabilidad

Toda consulta procesada por el bot debe quedar registrada para permitir auditoría y mejora del catálogo.

---

### RNF-22 — Mantenibilidad

El código debe organizarse en módulos según su responsabilidad.

No deben concentrarse todas las operaciones dentro de un único archivo.

---

### RNF-23 — Extensibilidad

El sistema debe permitir agregar:

* Nuevas categorías.
* Nuevas preguntas.
* Nuevas respuestas.
* Nuevos endpoints.
* Nuevas estadísticas.

sin modificar la lógica básica del bot.

---

### RNF-24 — Documentación de API

La API debe exponer documentación interactiva.

**Direcciones:**

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

### RNF-25 — Manejo de errores

El sistema debe manejar correctamente:

* Credenciales inválidas.
* Tokens vencidos.
* Recursos inexistentes.
* Registros duplicados.
* Base de datos no disponible.
* Backend no disponible.
* Telegram no disponible.
* Chat no configurado.
* Bot desactivado.
* Datos inválidos.

---

### RNF-26 — Configuración externa

Los parámetros que pueden cambiar entre ambientes deben definirse mediante variables de entorno.

---

### RNF-27 — Inicialización automática

La estructura y los datos iniciales de PostgreSQL deben crearse automáticamente al iniciar con un volumen nuevo.

---

### RNF-28 — Compatibilidad

El sistema debe poder ejecutarse en sistemas compatibles con Docker, incluyendo Linux, Windows y macOS.

---

### RNF-29 — Control de versiones

El código debe administrarse mediante Git y publicarse en GitHub.

El historial debe contener varios commits progresivos y descriptivos.

---

### RNF-30 — Disponibilidad de evidencia

La documentación debe incluir capturas que demuestren:

* Login.
* CRUD.
* Telegram.
* Historial.
* Estadísticas.
* Configuración.
* Contenedores.
* Base de datos.

---

## 6. Reglas de negocio

### RN-01

Cada pregunta debe pertenecer a una categoría.

### RN-02

Una pregunta puede tener como máximo una respuesta.

### RN-03

Solo las categorías activas deben participar en la operación normal del bot.

### RN-04

Solo las preguntas activas deben utilizarse durante la búsqueda.

### RN-05

Solo las respuestas activas deben enviarse a los usuarios.

### RN-06

El bot debe buscar primero una coincidencia exacta.

### RN-07

La búsqueda aproximada solo debe utilizarse cuando no exista coincidencia exacta.

### RN-08

Una coincidencia aproximada debe alcanzar una confianza mínima de `0.68`.

### RN-09

Toda consulta debe registrarse, incluso cuando no tenga respuesta.

### RN-10

Las consultas desconocidas deben utilizar el mensaje configurado en PostgreSQL.

### RN-11

La contraseña administrativa debe almacenarse mediante hash.

### RN-12

El token de Telegram no debe almacenarse en PostgreSQL.

### RN-13

El token de Telegram debe obtenerse desde variables de entorno.

### RN-14

El bot no debe contener respuestas estáticas dentro de su código.

### RN-15

La eliminación de una pregunta debe eliminar su respuesta asociada.

### RN-16

Los registros del historial deben conservar la respuesta enviada.

### RN-17

El sistema debe iniciar con al menos 20 preguntas y 3 categorías.

### RN-18

SmartBot solo debe responder información administrativa.

### RN-19

El sistema no debe realizar diagnósticos médicos.

### RN-20

El sistema no debe recomendar medicamentos o tratamientos.

---

## 7. Restricciones

* Se requiere conexión a Internet para Telegram.
* El bot depende de la disponibilidad de la API de Telegram.
* El sistema debe ejecutarse mediante Docker Compose.
* PostgreSQL es la fuente principal de información.
* El bot no puede acceder directamente a PostgreSQL.
* El frontend no puede acceder directamente a PostgreSQL.
* Los secretos no deben versionarse.
* La aplicación está orientada a consultas administrativas hospitalarias.

---

## 8. Criterios generales de aceptación

El sistema se considera funcional cuando:

1. Los cuatro contenedores se encuentran activos.
2. El health check indica conexión con PostgreSQL.
3. El administrador puede iniciar sesión.
4. El panel muestra 5 categorías, 20 preguntas y 20 respuestas.
5. El CRUD de categorías funciona.
6. El CRUD de preguntas funciona.
7. El CRUD de respuestas funciona.
8. Telegram recibe preguntas.
9. Una consulta exacta obtiene respuesta.
10. Una consulta aproximada obtiene respuesta.
11. Una consulta desconocida se rechaza correctamente.
12. Las tres consultas aparecen en el historial.
13. El dashboard actualiza sus estadísticas.
14. El chat ID puede configurarse desde el panel.
15. El mensaje de prueba llega a Telegram.
16. El token de Telegram no aparece en Git.
17. La aplicación puede reconstruirse mediante Docker Compose.