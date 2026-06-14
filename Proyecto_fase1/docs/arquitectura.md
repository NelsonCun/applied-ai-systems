# Arquitectura del sistema — Doctor Byte

## 1. Vista general

![Vista general de la arquitectura](./evidencias/Vista%20General.png)

## 2. Vista por capas

![Vista por capas](./evidencias/Diagrama%20de%20Arquitectura.png)

## 3. Responsabilidades

### Frontend

- Presenta síntomas dinámicos.
- Envía solicitudes REST.
- Muestra diagnóstico, recomendación e historial.
- Proporciona formularios administrativos.
- No contiene el token de Telegram ni la lógica de inferencia.

### Backend

- Valida entradas con Pydantic.
- Expone endpoints organizados por responsabilidad.
- Coordina Prolog, archivos operativos y Telegram.
- Traduce errores a respuestas HTTP controladas.

### Prolog

- Mantiene hechos y reglas.
- Cuenta coincidencias entre síntomas.
- Genera candidatos de diagnóstico.
- Selecciona un resultado determinista.
- Produce JSON para Python.

### Persistencia local

- `conocimiento.pl`: fuente de verdad del sistema experto.
- `historial.json`: resultados ejecutados.
- `configuracion.json`: opciones del bot.
- `.env`: secreto del bot e ID inicial.

### Telegram

- `getUpdates`: recepción mediante long polling.
- `getMe`: comprobación del bot.
- `sendMessage`: respuestas y notificaciones.

## 4. Secuencia de diagnóstico web

![Secuencia de diagnóstico web](./evidencias/Diagrama%20sin%20título.png)

## 5. Secuencia de Telegram

![Secuencia de Telegram](./evidencias/Flujo_interaccion_telegram.png)

## 6. Decisiones de diseño

- Prolog es la fuente de conocimiento; no se utilizó una base de datos adicional.
- El backend usa capas para aislar rutas, validación, integración y persistencia.
- El frontend se divide en vistas para mantener responsabilidades claras.
- La API de Telegram se consume directamente mediante HTTP.
- El historial y la configuración usan escritura atómica.
- La administración protege asociaciones y mínimos del proyecto.
