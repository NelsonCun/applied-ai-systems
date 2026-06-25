# Flujo de Ejecución de una Búsqueda

## Descripción

El siguiente diagrama representa el recorrido completo de una solicitud cuando el usuario ejecuta BFS, DFS o A*.

```mermaid
sequenceDiagram
    actor Usuario
    participant UI as Interfaz web
    participant API as FastAPI Router
    participant Pydantic as Modelos Pydantic
    participant Service as SearchService
    participant Algorithm as BFS / DFS / A*
    participant Common as Utilidades comunes

    Usuario->>UI: Configura inicio, destino y obstáculos
    Usuario->>UI: Selecciona un algoritmo

    UI->>API: POST /api/v1/search
    API->>Pydantic: Validar SearchRequest

    alt Configuración inválida
        Pydantic-->>API: Error de validación
        API-->>UI: HTTP 422
        UI-->>Usuario: Mostrar mensaje de error
    else Configuración válida
        Pydantic-->>API: Solicitud validada
        API->>Service: execute_search(request)
        Service->>Algorithm: Ejecutar algoritmo seleccionado

        loop Mientras existan nodos pendientes
            Algorithm->>Common: Obtener vecinos válidos
            Common-->>Algorithm: Arriba, derecha, abajo, izquierda
            Algorithm->>Algorithm: Extraer y registrar nodo explorado
        end

        alt Objetivo encontrado
            Algorithm->>Common: Reconstruir ruta
            Common-->>Algorithm: Ruta completa
        else No existe solución
            Algorithm->>Algorithm: Generar resultado sin ruta
        end

        Algorithm-->>Service: SearchOutcome
        Service-->>API: SearchResponse
        API-->>UI: HTTP 200 con JSON
        UI->>UI: Animar exploración y ruta
        UI-->>Usuario: Mostrar métricas y resultado
    end
```

## Orden de expansión

Los algoritmos utilizan un orden determinista de vecinos:

1. Arriba.
2. Derecha.
3. Abajo.
4. Izquierda.

No se permiten movimientos diagonales.

## Criterio de nodo explorado

Un nodo se considera explorado cuando es extraído de la estructura de frontera para ser procesado:

- BFS: al retirarlo de la cola.
- DFS: al retirarlo de la pila.
- A*: al retirarlo de la cola de prioridad y aceptarlo como nodo no cerrado.

## Longitud de la ruta

La longitud se calcula como:

```text
longitud = cantidad de coordenadas de la ruta - 1
```

Ejemplo:

```text
(0, 0) → (0, 1) → (0, 2)
```

La ruta contiene tres coordenadas, pero representa dos movimientos.
