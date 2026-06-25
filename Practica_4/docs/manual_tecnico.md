# Manual Técnico de RoboMaze



## Información general

| Campo | Valor |
|---|---|
| Lenguaje principal | Python 3 |
| Framework backend | FastAPI |
| Frontend | HTML, CSS y JavaScript |
| Control de versiones | Git y GitHub |

---

## 1. Introducción

RoboMaze es una aplicación web para crear, editar, resolver y comparar laberintos bidimensionales mediante algoritmos clásicos de búsqueda.

El sistema permite configurar una cuadrícula con:

- Una posición inicial.
- Una posición objetivo.
- Obstáculos.
- Dimensiones variables.

Posteriormente, el usuario puede ejecutar:

- Breadth-First Search.
- Depth-First Search.
- A*.

La aplicación muestra:

- El orden de exploración.
- La ruta encontrada.
- La longitud de la ruta.
- La cantidad de nodos explorados.
- El tiempo de ejecución.
- Una comparación entre algoritmos.

La lógica de búsqueda se ejecuta en el backend. El frontend gestiona la interacción, consume la API REST y visualiza los resultados.

---

## 2. Objetivos técnicos

### 2.1 Objetivo general

Desarrollar una aplicación web capaz de representar laberintos mediante una cuadrícula bidimensional y resolverlos utilizando algoritmos de búsqueda implementados manualmente en Python.

### 2.2 Objetivos específicos

- Implementar BFS mediante una cola FIFO.
- Implementar DFS mediante una pila LIFO.
- Implementar A* mediante una cola de prioridad.
- Utilizar distancia Manhattan como heurística.
- Separar la interfaz gráfica de la lógica de búsqueda.
- Exponer los casos de uso mediante una API REST.
- Comparar los algoritmos mediante métricas cuantitativas.
- Manejar laberintos solucionables y sin solución.
- Incluir escenarios predefinidos.
- Permitir generación automática.
- Exportar resultados a CSV y PDF.
- Permitir guardar e importar laberintos en JSON.
- Verificar el comportamiento mediante pruebas automatizadas.

---

## 3. Alcance

RoboMaze permite trabajar con laberintos rectangulares de entre 5 y 40 filas y columnas desde la interfaz.

Cada celda puede representar:

- Celda libre.
- Obstáculo.
- Inicio.
- Destino.
- Nodo explorado.
- Parte de la ruta.

El sistema utiliza movimientos en cuatro direcciones:

- Arriba.
- Derecha.
- Abajo.
- Izquierda.

No se permiten movimientos diagonales.

El proyecto no utiliza base de datos. Los laberintos predefinidos se almacenan en código y los archivos se procesan bajo demanda.

---

## 4. Requerimientos funcionales

| Código | Requerimiento |
|---|---|
| RF-01 | El sistema deberá representar el laberinto mediante una cuadrícula bidimensional. |
| RF-02 | El usuario deberá poder configurar filas y columnas. |
| RF-03 | El usuario deberá poder establecer una única posición inicial. |
| RF-04 | El usuario deberá poder establecer una única posición objetivo. |
| RF-05 | El usuario deberá poder agregar obstáculos. |
| RF-06 | El usuario deberá poder eliminar obstáculos. |
| RF-07 | El sistema deberá impedir obstáculos sobre el inicio. |
| RF-08 | El sistema deberá impedir obstáculos sobre el objetivo. |
| RF-09 | El inicio y el objetivo deberán ser diferentes. |
| RF-10 | El backend deberá ejecutar BFS de forma independiente. |
| RF-11 | El backend deberá ejecutar DFS de forma independiente. |
| RF-12 | El backend deberá ejecutar A* de forma independiente. |
| RF-13 | El sistema deberá mostrar la ruta encontrada. |
| RF-14 | El sistema deberá mostrar el orden de exploración. |
| RF-15 | El sistema deberá mostrar la longitud de la ruta. |
| RF-16 | El sistema deberá mostrar los nodos explorados. |
| RF-17 | El sistema deberá mostrar el tiempo de ejecución. |
| RF-18 | El sistema deberá comparar BFS, DFS y A*. |
| RF-19 | La comparación deberá usar el mismo laberinto. |
| RF-20 | La comparación deberá mostrar ruta, nodos y tiempo. |
| RF-21 | El sistema deberá manejar laberintos sin solución. |
| RF-22 | El sistema deberá incluir al menos cinco laberintos solucionables. |
| RF-23 | El sistema deberá incluir un escenario sin solución. |
| RF-24 | El sistema deberá generar laberintos aleatorios. |
| RF-25 | Los laberintos generados deberán tener una ruta garantizada. |
| RF-26 | La generación deberá aceptar densidad de obstáculos. |
| RF-27 | La generación deberá aceptar una semilla opcional. |
| RF-28 | Una misma semilla deberá reproducir el mismo laberinto. |
| RF-29 | El usuario deberá poder seleccionar la velocidad de animación. |
| RF-30 | El usuario deberá poder limpiar la visualización del resultado. |
| RF-31 | El usuario deberá poder vaciar el laberinto. |
| RF-32 | El usuario deberá poder guardar el laberinto en JSON. |
| RF-33 | El usuario deberá poder importar un laberinto desde JSON. |
| RF-34 | El sistema deberá validar los archivos JSON importados. |
| RF-35 | El usuario deberá poder exportar resultados a CSV. |
| RF-36 | El usuario deberá poder descargar un reporte PDF. |
| RF-37 | El PDF deberá incluir laberinto, métricas, comparación y ruta. |
| RF-38 | El backend deberá exponer una API REST. |
| RF-39 | La API deberá incluir documentación OpenAPI. |
| RF-40 | El sistema deberá ofrecer un endpoint de estado. |

---

## 5. Requerimientos no funcionales

| Código | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | Rendimiento | Las búsquedas deberán ejecutarse en memoria. |
| RNF-02 | Rendimiento | El sistema deberá soportar cuadrículas de hasta 40 por 40. |
| RNF-03 | Usabilidad | La interfaz deberá diferenciar visualmente cada estado de celda. |
| RNF-04 | Usabilidad | Los errores deberán mostrarse mediante mensajes comprensibles. |
| RNF-05 | Usabilidad | Las acciones deberán tener etiquetas claras. |
| RNF-06 | Mantenibilidad | Presentación, servicios y algoritmos deberán permanecer separados. |
| RNF-07 | Mantenibilidad | Cada algoritmo deberá estar en su propio módulo. |
| RNF-08 | Testabilidad | Algoritmos, API, validaciones y reportes deberán tener pruebas. |
| RNF-09 | Portabilidad | La aplicación deberá ejecutarse en Python 3. |
| RNF-10 | Compatibilidad | El frontend deberá funcionar en navegadores modernos. |
| RNF-11 | Fiabilidad | Los laberintos solucionables deberán verificarse mediante pruebas. |
| RNF-12 | Fiabilidad | La generación automática deberá garantizar una ruta. |
| RNF-13 | Seguridad | Las entradas de la API deberán validarse mediante Pydantic. |
| RNF-14 | Seguridad | Las coordenadas fuera de rango deberán rechazarse. |
| RNF-15 | Escalabilidad | La arquitectura deberá permitir nuevos algoritmos. |
| RNF-16 | Accesibilidad | Los controles deberán tener foco visible y etiquetas. |
| RNF-17 | Consistencia | El orden de vecinos deberá ser determinista. |
| RNF-18 | Trazabilidad | El repositorio deberá conservar commits progresivos. |

---

## 6. Tecnologías

### Backend

- Python 3.12.
- FastAPI.
- Uvicorn.
- Pydantic.
- ReportLab.
- `collections.deque`.
- `heapq`.
- `time.perf_counter_ns`.

### Frontend

- HTML5.
- CSS3.
- JavaScript.
- Fetch API.
- JavaScript ES Modules.
- Blob y Object URL.

### Pruebas

- Pytest.
- FastAPI TestClient.
- HTTPX.

### Herramientas

- Git.
- GitHub.
- Entorno virtual de Python.
- Swagger UI.

---

## 7. Arquitectura

![Arquitectura de RoboMaze](./diagramas/Diagrama%20de%20arquitectura.png)

RoboMaze utiliza una **arquitectura monolítica en capas**. La aplicación se despliega como un único servicio construido con FastAPI, pero su código se encuentra dividido en componentes con responsabilidades específicas.

Este patrón evita que la interfaz gráfica, los endpoints, los servicios y los algoritmos de búsqueda se encuentren mezclados. Cada capa conoce únicamente los componentes necesarios de la capa inferior, lo que facilita el mantenimiento, las pruebas y la incorporación de nuevas funcionalidades.

### Capa de presentación

La capa de presentación está formada por la interfaz web de RoboMaze, desarrollada con HTML, CSS y JavaScript.

Sus archivos principales se encuentran en:

```text
app/static/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── api.js
    └── app.js
```

Esta capa se encarga de:

* Representar visualmente el laberinto mediante una cuadrícula.
* Recibir las acciones del usuario.
* Permitir la selección del punto inicial y del destino.
* Permitir la colocación y eliminación de obstáculos.
* Mostrar la exploración realizada por cada algoritmo.
* Animar la ruta encontrada.
* Presentar la longitud de la ruta, los nodos explorados y el tiempo de ejecución.
* Mostrar la comparación entre BFS, DFS y A*.
* Guardar e importar configuraciones en formato JSON.
* Descargar resultados en formato CSV.
* Solicitar la generación del reporte PDF al backend.

La interfaz no implementa los algoritmos de búsqueda. Su responsabilidad se limita a la interacción con el usuario, el envío de solicitudes y la visualización de los resultados.

La comunicación con el backend se realiza mediante solicitudes HTTP y respuestas JSON utilizando la API `fetch` de JavaScript.

---

### Capa de API REST

La capa de API REST constituye el punto de entrada al backend.

Su implementación principal se encuentra en:

```text
app/api/routes.py
```

Esta capa utiliza FastAPI para exponer los endpoints del sistema bajo el prefijo:

```text
/api/v1
```

Sus responsabilidades son:

* Recibir las solicitudes HTTP enviadas por la interfaz.
* Identificar el endpoint solicitado.
* Validar los datos de entrada.
* Delegar la operación al servicio correspondiente.
* Serializar las respuestas.
* Devolver respuestas JSON o archivos PDF.
* Proporcionar documentación automática mediante OpenAPI y Swagger.

Entre los endpoints principales se encuentran:

```http
GET  /api/v1/health
POST /api/v1/search
POST /api/v1/search/compare
GET  /api/v1/mazes
GET  /api/v1/mazes/{maze_id}
POST /api/v1/mazes/generate
POST /api/v1/reports/pdf
```

La API no contiene directamente la implementación de BFS, DFS o A*. Su función es recibir la solicitud, validarla y transferirla hacia la capa de servicios.

---

### Modelos y validación

Los contratos de entrada y salida se definen mediante modelos Pydantic ubicados en:

```text
app/models/schemas.py
```

Estos modelos representan estructuras como:

* Coordenadas.
* Configuración del laberinto.
* Solicitud de búsqueda.
* Resultado de búsqueda.
* Comparación de algoritmos.
* Solicitud de generación automática.
* Solicitud de reporte PDF.

La validación permite comprobar:

* Que las dimensiones del tablero sean válidas.
* Que las coordenadas estén dentro de los límites.
* Que el inicio y el destino sean diferentes.
* Que no existan obstáculos repetidos.
* Que los obstáculos no ocupen el inicio o el destino.
* Que el algoritmo solicitado esté soportado.
* Que la densidad de obstáculos se encuentre dentro del rango permitido.
* Que exista información válida antes de generar un reporte.

Esta validación se ejecuta antes de que la solicitud llegue a la lógica de negocio.

---

### Capa de servicios de aplicación

La capa de servicios coordina los casos de uso del sistema.

Se encuentra en:

```text
app/services/
├── search_service.py
├── maze_service.py
└── report_service.py
```

#### SearchService

`search_service.py` coordina la ejecución de los algoritmos de búsqueda.

Sus funciones principales son:

* Seleccionar BFS, DFS o A*.
* Transformar la configuración recibida al formato utilizado por los algoritmos.
* Ejecutar una búsqueda individual.
* Ejecutar los tres algoritmos sobre el mismo laberinto.
* Construir las respuestas con las métricas obtenidas.
* Proporcionar los datos necesarios para la comparación.

Las métricas comparativas se obtienen a partir de los resultados generados por este servicio. La interfaz se encarga posteriormente de representarlas mediante tablas y gráficas.

#### MazeService

`maze_service.py` administra los laberintos disponibles.

Sus responsabilidades son:

* Listar los escenarios predefinidos.
* Obtener un escenario por su identificador.
* Generar laberintos aleatorios.
* Aplicar una densidad de obstáculos.
* Utilizar una semilla para generar resultados reproducibles.
* Garantizar una ruta válida en los laberintos generados.

#### ReportService

`report_service.py` genera los documentos PDF.

Sus responsabilidades son:

* Recibir la configuración del laberinto.
* Recibir los resultados de búsqueda.
* Dibujar la cuadrícula dentro del documento.
* Incorporar métricas y comparación.
* Mostrar la ruta completa.
* Agregar leyenda y numeración de páginas.
* Devolver el contenido binario del archivo PDF.

Para construir el documento, este servicio utiliza la biblioteca ReportLab.

La exportación CSV se realiza en la capa de presentación, debido a que utiliza los resultados que ya fueron recibidos desde la API y no requiere procesamiento adicional del backend.

---

### Capa de dominio

La capa de dominio contiene la lógica principal del problema.

Se encuentra en:

```text
app/algorithms/
├── bfs.py
├── dfs.py
├── astar.py
└── common.py
```

Esta capa no depende de la interfaz gráfica ni de los detalles de HTTP. Recibe una representación del laberinto y devuelve el resultado de la búsqueda.

#### Breadth-First Search

`bfs.py` implementa BFS mediante una cola FIFO.

El algoritmo explora el laberinto por niveles y garantiza una ruta con la menor cantidad de movimientos cuando todos los desplazamientos tienen el mismo costo.

#### Depth-First Search

`dfs.py` implementa DFS mediante una pila LIFO.

El algoritmo profundiza en una alternativa antes de explorar otras rutas. Puede encontrar una solución válida, pero no garantiza que sea la ruta más corta.

#### A*

`astar.py` implementa A* mediante una cola de prioridad.

Utiliza la función:

```text
f(n) = g(n) + h(n)
```

La heurística empleada es la distancia Manhattan, adecuada para una cuadrícula en la que solamente se permiten movimientos verticales y horizontales.

#### Utilidades comunes

`common.py` contiene funciones compartidas por los algoritmos, entre ellas:

* Validación de posiciones.
* Obtención de vecinos transitables.
* Orden determinista de movimientos.
* Reconstrucción de la ruta.
* Estructuras comunes de resultados.

El orden de expansión utilizado es:

```text
Arriba → Derecha → Abajo → Izquierda
```

---

### Capa de datos estáticos

RoboMaze no utiliza una base de datos.

Los laberintos predefinidos se almacenan en:

```text
app/data/predefined_mazes.py
```

Esta capa contiene:

* Identificador del escenario.
* Nombre.
* Descripción.
* Dimensiones.
* Posición inicial.
* Posición objetivo.
* Obstáculos.

Los escenarios son consultados por `MazeService` y enviados a la interfaz mediante la API REST.

El uso de datos estáticos permite cumplir la restricción de no utilizar una base de datos para almacenar el estado del laberinto o los resultados.

Los archivos JSON guardados por el usuario permanecen en su equipo y no constituyen persistencia en el servidor.

---

### Capa de infraestructura y soporte

La capa de infraestructura contiene los elementos necesarios para ejecutar la aplicación.

Sus principales componentes son:

#### Servidor ASGI

Uvicorn ejecuta la aplicación FastAPI y atiende las solicitudes HTTP.

El punto de inicialización se encuentra en:

```text
app/main.py
```

Este archivo:

* Crea la instancia de FastAPI.
* Registra las rutas de la API.
* Configura los archivos estáticos.
* Entrega la página principal.
* Configura la documentación OpenAPI.

#### Archivos estáticos

FastAPI publica los archivos HTML, CSS y JavaScript desde:

```text
app/static/
```

Esto permite que la interfaz y la API se sirvan desde el mismo origen.

#### Manejo de errores

FastAPI y Pydantic proporcionan respuestas controladas ante solicitudes inválidas.

Por ejemplo:

* HTTP 404 para recursos inexistentes.
* HTTP 422 para errores de validación.
* Respuestas sin ruta cuando el laberinto no tiene solución.

#### Registro de ejecución

Uvicorn y FastAPI generan registros básicos de:

* Inicio y detención del servidor.
* Solicitudes HTTP.
* Códigos de respuesta.
* Errores de ejecución.

#### Generación de PDF

ReportLab funciona como una dependencia interna de infraestructura utilizada por `ReportService`. No se comunica con un servicio remoto ni envía información fuera de la aplicación.

---

## Flujo de una solicitud

El flujo general para ejecutar un algoritmo es el siguiente:

1. El usuario configura el laberinto desde la interfaz web.
2. JavaScript construye una solicitud con las dimensiones, inicio, destino y obstáculos.
3. La interfaz envía la solicitud a la API REST.
4. FastAPI recibe la solicitud en `routes.py`.
5. Pydantic valida la estructura y las reglas de los datos.
6. La ruta delega la operación a `SearchService`.
7. `SearchService` selecciona BFS, DFS o A*.
8. El algoritmo consulta las utilidades de `common.py`.
9. El algoritmo devuelve la ruta, exploración y métricas.
10. `SearchService` construye la respuesta.
11. La API serializa el resultado como JSON.
12. La interfaz recibe el resultado.
13. JavaScript anima la exploración y la ruta.
14. El panel de resultados muestra las métricas obtenidas.

El flujo para generar un reporte PDF es similar, pero la solicitud se delega a `ReportService`, que utiliza ReportLab y devuelve un archivo con tipo de contenido `application/pdf`.

---

## Dirección de las dependencias

Las dependencias siguen una dirección descendente:

```text
Presentación
    ↓
API REST
    ↓
Servicios de aplicación
    ↓
Dominio y algoritmos
    ↓
Datos estáticos e infraestructura
```

La capa de dominio no conoce la interfaz web ni los endpoints. Esto permite probar los algoritmos directamente sin iniciar el servidor o abrir el navegador.

De la misma manera, la interfaz no conoce los detalles internos de BFS, DFS o A*. Únicamente consume los contratos publicados por la API.

---

## Beneficios de la arquitectura

La arquitectura por capas proporciona los siguientes beneficios:

* **Separación de responsabilidades:** cada módulo tiene una función concreta.
* **Mantenibilidad:** los cambios visuales no afectan los algoritmos.
* **Testabilidad:** los algoritmos y servicios pueden probarse de forma independiente.
* **Extensibilidad:** es posible agregar nuevos algoritmos sin rediseñar toda la aplicación.
* **Reutilización:** las funciones comunes son compartidas por BFS, DFS y A*.
* **Validación centralizada:** Pydantic evita que datos incorrectos lleguen al dominio.
* **Bajo acoplamiento:** la comunicación se realiza mediante modelos y respuestas definidas.
* **Trazabilidad:** cada solicitud sigue un flujo claro desde la interfaz hasta el algoritmo.
* **Cumplimiento de restricciones:** la lógica de búsqueda permanece exclusivamente en el backend y no se utiliza una base de datos.

---

## 8. Estructura del proyecto

```text
Practica_4/
├── app/
│   ├── main.py
│   ├── algorithms/
│   │   ├── common.py
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   └── astar.py
│   ├── api/
│   │   └── routes.py
│   ├── data/
│   │   └── predefined_mazes.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── search_service.py
│   │   ├── maze_service.py
│   │   └── report_service.py
│   └── static/
│       ├── index.html
│       ├── css/
│       │   └── styles.css
│       └── js/
│           ├── api.js
│           └── app.js
├── docs/
│   ├── README.md
│   ├── manual_tecnico.md
│   ├── manual_usuario.md
│   ├── diagramas/
│   │   ├── arquitectura.md
│   │   └── flujo_busqueda.md
│   └── evidencias/
├── tests/
│   ├── test_api.py
│   ├── test_astar.py
│   ├── test_bfs.py
│   ├── test_dfs.py
│   ├── test_mazes.py
│   ├── test_reports.py
│   └── test_validations.py
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## 9. Modelos principales

### Coordinate

```json
{
  "row": 0,
  "column": 0
}
```

### MazeConfiguration

```json
{
  "rows": 8,
  "columns": 8,
  "start": {
    "row": 0,
    "column": 0
  },
  "goal": {
    "row": 7,
    "column": 7
  },
  "obstacles": [
    {
      "row": 2,
      "column": 1
    }
  ]
}
```

### SearchRequest

Algoritmos permitidos:

```text
bfs
dfs
astar
```

### SearchResponse

Incluye:

- Algoritmo.
- Nombre.
- Estado.
- Ruta.
- Exploración.
- Longitud.
- Nodos.
- Tiempo.
- Mensaje.

### ComparisonResponse

Agrupa resultados de BFS, DFS y A*.

### GenerateMazeRequest

Incluye filas, columnas, densidad y semilla.

### PdfReportRequest

Incluye laberinto, resultado y comparación.

---

## 10. Representación interna

Las posiciones se representan como:

```python
(row, column)
```

Los obstáculos utilizan:

```python
set[tuple[int, int]]
```

Orden de movimientos:

```python
DIRECTIONS = (
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1),
)
```

---

## 11. Breadth-First Search

BFS explora por niveles y utiliza una cola FIFO.

Estructuras:

- `deque`.
- Conjunto de descubiertos.
- Diccionario de padres.
- Lista de exploración.

Cuando todos los movimientos cuestan uno, BFS garantiza una ruta mínima.

```text
Tiempo: O(V + E)
Espacio: O(V)
```

---

## 12. Depth-First Search

DFS profundiza en una rama mediante una pila LIFO.

No garantiza la ruta más corta.

```text
Tiempo: O(V + E)
Espacio: O(V)
```

---

## 13. A*

A* utiliza:

```text
f(n) = g(n) + h(n)
```

La heurística es Manhattan:

```text
h(n) = |fila_actual - fila_objetivo|
     + |columna_actual - columna_objetivo|
```

```text
Tiempo aproximado: O((V + E) log V)
Espacio: O(V)
```

---

## 14. Reconstrucción de ruta

Los algoritmos registran el padre de cada posición. Al encontrar la meta, recorren los padres en sentido inverso y luego invierten la lista.

```text
longitud = cantidad de coordenadas - 1
```

---

## 15. Nodos explorados

Un nodo se considera explorado cuando se extrae de la frontera para ser procesado.

---

## 16. Medición del tiempo

Se utiliza:

```python
time.perf_counter_ns()
```

El resultado se convierte a milisegundos.

---

## 17. Laberintos predefinidos

| ID | Nombre | Dimensiones | Solución |
|---|---|---:|---|
| `basic` | Introducción | 8 × 8 | Sí |
| `detour` | Desvío obligatorio | 10 × 10 | Sí |
| `corridors` | Corredores alternados | 12 × 12 | Sí |
| `multiple-routes` | Múltiples rutas | 10 × 14 | Sí |
| `large` | Exploración amplia | 20 × 20 | Sí |
| `no-solution` | Objetivo aislado | 8 × 8 | No |

---

## 18. Generación automática

La generación recibe filas, columnas, densidad y semilla.

Para garantizar una ruta, protege:

- La primera fila.
- La última columna.

---

## 19. API REST

Base local:

```text
http://127.0.0.1:8002/api/v1
```

Swagger:

```text
http://127.0.0.1:8002/docs
```

### Endpoints

```http
GET /api/v1/health
POST /api/v1/search
POST /api/v1/search/compare
GET /api/v1/mazes
GET /api/v1/mazes/{maze_id}
POST /api/v1/mazes/generate
POST /api/v1/reports/pdf
```

### Ejemplo de búsqueda

```json
{
  "algorithm": "bfs",
  "rows": 5,
  "columns": 5,
  "start": {
    "row": 0,
    "column": 0
  },
  "goal": {
    "row": 4,
    "column": 4
  },
  "obstacles": [
    {
      "row": 1,
      "column": 1
    }
  ]
}
```

---

## 20. Códigos HTTP

| Código | Significado |
|---:|---|
| 200 | Operación correcta |
| 404 | Recurso no encontrado |
| 422 | Error de validación |
| 500 | Error interno |

---

## 21. Validaciones

- Dimensiones.
- Coordenadas.
- Límites.
- Inicio distinto del objetivo.
- Obstáculos no repetidos.
- Obstáculos fuera de inicio y destino.
- Algoritmo válido.
- Densidad válida.
- Reporte con contenido.

---

## 22. Frontend

### api.js

Centraliza las solicitudes HTTP.

### app.js

Gestiona:

- Estado.
- Renderizado.
- Edición.
- Animación.
- Métricas.
- Gráficas.
- JSON.
- CSV.
- PDF.

### styles.css

Define:

- Tema azul oscuro.
- Distribución.
- Estados semánticos.
- Diseño responsivo.
- Foco visual.

---

## 23. Persistencia local

Formato de guardado:

```json
{
  "format": "robomaze-maze",
  "version": 1,
  "saved_at": "fecha ISO",
  "maze": {}
}
```

---

## 24. Exportación CSV

Columnas:

- Algoritmo.
- Estado.
- Longitud.
- Nodos explorados.
- Tiempo.
- Ruta completa.

---

## 25. Reporte PDF

Se genera con ReportLab e incluye:

- Configuración.
- Métricas.
- Laberinto.
- Leyenda.
- Comparación.
- Ruta.
- Paginación.

---

## 26. Pruebas automatizadas

El proyecto contiene 23 pruebas.

```bash
cd Practica_4
source .venv/bin/activate
pytest
```

---

## 27. Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 28. Ejecución

```bash
python -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8002 \
  --reload
```

Interfaz:

```text
http://127.0.0.1:8002
```

---

## 29. Manejo de errores

- HTTP 422 para configuraciones inválidas.
- HTTP 404 para laberintos inexistentes.
- Resultado controlado cuando no existe solución.
- Mensaje visible cuando la API no está disponible.
- Rechazo de archivos JSON inválidos.

---

## 30. Decisiones de diseño

- Los algoritmos se ejecutan en Python.
- No se utiliza base de datos.
- El frontend consume rutas relativas.
- El orden de vecinos es determinista.
- A* se incorporó como funcionalidad adicional.

---

## 31. Limitaciones

- Sin persistencia en servidor.
- Sin autenticación.
- Un inicio.
- Un objetivo.
- Movimientos con costo uno.
- Sin diagonales.
- Sin obstáculos dinámicos.
- Comparación secuencial.

---

## 32. Mejoras futuras

- Dijkstra.
- Greedy Best-First Search.
- Costos por celda.
- Movimientos diagonales.
- Múltiples objetivos.
- Obstáculos dinámicos.
- Generación por backtracking.
- Prim o Kruskal.
- Historial de resultados.
- Estadísticas acumuladas.
- Pruebas end-to-end.
- Docker.
- Despliegue en nube.

---

## 33. Conclusiones (1 por cada objetivo específico)
* RoboMaze es una herramienta educativa valiosa que combina teoría y práctica, permitiendo a los estudiantes y entusiastas de la inteligencia artificial explorar conceptos fundamentales de algoritmos de búsqueda de manera interactiva y visual, fomentando un aprendizaje más profundo y significativo.
* La implementación de algoritmos como BFS, DFS y A* permite a los usuarios observar las diferencias en la exploración y la eficiencia de cada algoritmo, destacando sus fortalezas y debilidades en distintos escenarios.
* La capacidad de generar laberintos automáticamente y guardar/importar configuraciones en formato JSON ofrece flexibilidad y conveniencia para los usuarios, permitiéndoles experimentar con diferentes configuraciones y escenarios.
* La funcionalidad de exportar resultados en formatos CSV y PDF proporciona una manera efectiva de documentar y analizar los resultados de las búsquedas, facilitando la comparación y el estudio de los algoritmos.
* El proyecto maneja adecuadamente los errores y situaciones sin solución, asegurando que los usuarios reciban retroalimentación clara y puedan tomar decisiones informadas sobre cómo modificar el laberinto o los parámetros de búsqueda.
* En general, RoboMaze es una herramienta educativa valiosa que combina teoría y práctica, permitiendo a los estudiantes y entusiastas de la inteligencia artificial explorar conceptos fundamentales de algoritmos de búsqueda de manera interactiva y visual, fomentando un aprendizaje más profundo y significativo.