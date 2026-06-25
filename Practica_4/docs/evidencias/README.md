# Evidencias del Manual de Usuario

Este directorio almacena las capturas utilizadas por:

```text
docs/manual_usuario.md
```

## Formato recomendado

- Formato: PNG.
- Resolución mínima: 1366 × 768.
- Navegador maximizado.
- Zoom del navegador: 80 % o 90 % cuando sea necesario.
- Sin terminales, notificaciones ni datos ajenos visibles.
- No recortar información importante.
- Mantener el mismo tema visual en todas las capturas.

## Archivos requeridos

| Archivo | Contenido esperado |
|---|---|
| `01_pantalla_principal.png` | Interfaz completa recién cargada |
| `02_leyenda_cuadricula.png` | Cuadrícula y leyenda visibles |
| `03_abrir_escenario.png` | Escenario seleccionado y cargado |
| `04_crear_tablero.png` | Tablero con dimensiones personalizadas |
| `05_edicion_manual.png` | Obstáculos, inicio y destino editados |
| `06_resultado_bfs.png` | BFS finalizado con métricas |
| `07_resultado_dfs.png` | DFS finalizado con métricas |
| `08_resultado_astar.png` | A* finalizado con métricas |
| `09_comparacion_algoritmos.png` | Tabla y gráficas comparativas |
| `10_sin_solucion.png` | Escenario imposible y estado sin solución |
| `11_generacion_automatica.png` | Laberinto generado automáticamente |
| `12_guardar_json.png` | Confirmación o archivo JSON descargado |
| `13_importar_json.png` | Laberinto restaurado desde JSON |
| `14_exportar_csv.png` | Archivo CSV abierto o descarga visible |
| `15_descargar_pdf.png` | Confirmación de descarga desde la interfaz |
| `16_reporte_pdf.png` | PDF abierto y legible |
| `17_swagger.png` | Swagger UI con endpoints visibles |

## Secuencia recomendada para capturas

### Preparación

1. Inicie Uvicorn en el puerto `8002`.
2. Abra `http://127.0.0.1:8002`.
3. Maximice el navegador.
4. Use `Ctrl + Shift + R`.
5. Ajuste el zoom.

### Capturas generales

1. Tome `01_pantalla_principal.png`.
2. Asegúrese de que la cuadrícula y la leyenda estén visibles.
3. Tome `02_leyenda_cuadricula.png`.

### Escenarios y edición

1. Seleccione **Múltiples rutas**.
2. Presione **Abrir escenario**.
3. Tome `03_abrir_escenario.png`.
4. Cree un tablero de 12 × 16.
5. Tome `04_crear_tablero.png`.
6. Agregue obstáculos y cambie inicio y destino.
7. Tome `05_edicion_manual.png`.

### Algoritmos

Use preferentemente **Múltiples rutas**:

1. Ejecute BFS y tome `06_resultado_bfs.png`.
2. Limpie el resultado.
3. Ejecute DFS y tome `07_resultado_dfs.png`.
4. Limpie el resultado.
5. Ejecute A* y tome `08_resultado_astar.png`.
6. Presione **Comparar**.
7. Asegúrese de que tabla y gráficas estén visibles.
8. Tome `09_comparacion_algoritmos.png`.

### Sin solución

1. Abra **Objetivo aislado**.
2. Ejecute BFS.
3. Espere el mensaje final.
4. Tome `10_sin_solucion.png`.

### Generación automática

Use:

```text
Filas: 15
Columnas: 20
Densidad: 25 %
Semilla: 2026
```

Tome `11_generacion_automatica.png`.

### JSON

1. Presione **Guardar laberinto**.
2. Tome `12_guardar_json.png`.
3. Cambie o vacíe el tablero.
4. Importe el archivo guardado.
5. Tome `13_importar_json.png`.

### CSV y PDF

1. Ejecute una comparación.
2. Descargue el CSV.
3. Ábralo con una aplicación apropiada.
4. Tome `14_exportar_csv.png`.
5. Descargue el PDF.
6. Tome `15_descargar_pdf.png`.
7. Abra el PDF.
8. Tome `16_reporte_pdf.png`.

### Swagger

1. Abra `http://127.0.0.1:8002/docs`.
2. Asegúrese de que se vean los endpoints.
3. Tome `17_swagger.png`.

## Captura en Ubuntu

Puede usar la herramienta integrada:

```text
Impr Pant
```

También puede utilizar:

```bash
gnome-screenshot -i
```

Si utiliza Flameshot:

```bash
flameshot gui
```

## Verificación

Después de agregar las imágenes:

```bash
find docs/evidencias \
  -maxdepth 1 \
  -type f \
  | sort
```

Deben existir las 17 capturas y `.gitkeep`.

Compruebe referencias rotas:

```bash
python3 - <<'PY'
from pathlib import Path
import re

manual = Path("docs/manual_usuario.md")
content = manual.read_text(encoding="utf-8")

references = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)

missing = []

for reference in references:
    target = manual.parent / reference
    status = "EXISTE" if target.exists() else "FALTA"

    print(f"{status:6} | {reference}")

    if not target.exists():
        missing.append(reference)

if missing:
    raise SystemExit(
        f"Faltan {len(missing)} imágenes."
    )

print("\nTodas las evidencias existen.")
PY
```
