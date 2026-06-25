# Diagrama de Arquitectura de RoboMaze

## Descripción general

RoboMaze utiliza una **arquitectura monolítica en capas**. La aplicación se ejecuta como un único servicio FastAPI, pero sus responsabilidades se encuentran separadas en módulos independientes.

Las capas principales son:

1. Presentación.
2. API REST.
3. Modelos y validación.
4. Servicios de aplicación.
5. Dominio de búsqueda.
6. Datos estáticos e infraestructura.

## Diagrama

```mermaid
flowchart LR
    subgraph CLIENTE["Cliente web"]
        USUARIO["Usuario"]
        UI["Interfaz web<br/>HTML + CSS + JavaScript"]
        ARCHIVOS["Archivos locales<br/>JSON · CSV · PDF"]
    end

    subgraph SERVIDOR["Aplicación FastAPI"]
        MAIN["app/main.py<br/>Inicialización y archivos estáticos"]

        subgraph API["Capa de API REST"]
            ROUTES["app/api/routes.py<br/>Endpoints HTTP"]
        end

        subgraph MODELOS["Capa de modelos y validación"]
            SCHEMAS["app/models/schemas.py<br/>Modelos Pydantic"]
        end

        subgraph SERVICIOS["Capa de servicios"]
            SEARCH_SERVICE["search_service.py<br/>Ejecución y comparación"]
            MAZE_SERVICE["maze_service.py<br/>Catálogo y generación"]
            REPORT_SERVICE["report_service.py<br/>Generación de PDF"]
        end

        subgraph DOMINIO["Dominio de búsqueda"]
            COMMON["common.py<br/>Vecinos y reconstrucción"]
            BFS["bfs.py<br/>Breadth-First Search"]
            DFS["dfs.py<br/>Depth-First Search"]
            ASTAR["astar.py<br/>A* con Manhattan"]
        end

        subgraph DATOS["Datos estáticos"]
            MAZES["predefined_mazes.py<br/>Laberintos predefinidos"]
        end

        subgraph INFRA["Infraestructura"]
            REPORTLAB["ReportLab<br/>Generación de documentos PDF"]
            STATIC["Archivos estáticos<br/>index.html · CSS · JavaScript"]
        end
    end

    USUARIO --> UI

    UI -- "GET /" --> MAIN
    MAIN --> STATIC
    STATIC --> UI

    UI -- "Solicitudes HTTP con JSON" --> ROUTES
    ROUTES --> SCHEMAS

    ROUTES --> SEARCH_SERVICE
    ROUTES --> MAZE_SERVICE
    ROUTES --> REPORT_SERVICE

    SEARCH_SERVICE --> BFS
    SEARCH_SERVICE --> DFS
    SEARCH_SERVICE --> ASTAR

    BFS --> COMMON
    DFS --> COMMON
    ASTAR --> COMMON

    MAZE_SERVICE --> MAZES
    REPORT_SERVICE --> REPORTLAB

    ROUTES -- "JSON o PDF" --> UI
    UI --> ARCHIVOS
```

## Responsabilidad de cada capa

### Presentación

Ubicación:

```text
app/static/
```

Responsabilidades:

- Mostrar el laberinto.
- Recibir acciones del usuario.
- Construir solicitudes HTTP.
- Consumir la API REST.
- Animar la exploración y la ruta.
- Mostrar métricas.
- Gestionar archivos JSON.
- Descargar resultados CSV y PDF.

### API REST

Ubicación:

```text
app/api/routes.py
```

Responsabilidades:

- Exponer endpoints HTTP.
- Recibir solicitudes.
- Aplicar validaciones.
- Delegar los casos de uso.
- Devolver respuestas JSON o archivos PDF.

### Modelos y validación

Ubicación:

```text
app/models/schemas.py
```

Responsabilidades:

- Validar dimensiones.
- Validar coordenadas.
- Verificar inicio y destino.
- Detectar obstáculos repetidos.
- Definir contratos de entrada y salida.

### Servicios de aplicación

Ubicación:

```text
app/services/
```

Responsabilidades:

- Coordinar la ejecución de algoritmos.
- Comparar BFS, DFS y A*.
- Administrar laberintos predefinidos.
- Generar laberintos aleatorios.
- Construir reportes PDF.

### Dominio

Ubicación:

```text
app/algorithms/
```

Responsabilidades:

- Implementar BFS.
- Implementar DFS.
- Implementar A*.
- Obtener vecinos válidos.
- Reconstruir rutas.
- Estandarizar resultados.

### Datos estáticos

Ubicación:

```text
app/data/predefined_mazes.py
```

Responsabilidades:

- Definir el catálogo de laberintos.
- Almacenar metadatos y obstáculos.
- Evitar el uso de base de datos.

## Justificación

La arquitectura en capas permite:

- Separar la interfaz de los algoritmos.
- Probar los algoritmos de manera independiente.
- Agregar nuevos algoritmos sin reescribir la API.
- Sustituir la interfaz sin modificar el dominio.
- Mantener validaciones centralizadas.
- Incorporar nuevos formatos de exportación.
