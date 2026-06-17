# Lote de validación de 20 facturas

Este directorio contiene un lote sintético utilizado para validar el
procesamiento masivo de SmartInvoice.

## Contenido

- 20 facturas únicas.
- Formatos PDF, PNG y JPG.
- Cinco proveedores previamente registrados.
- Fechas válidas de mayo de 2026.
- Subtotal, IVA del 12% y total consistente.
- Variaciones leves de ruido, contraste y rotación.
- Resultados esperados en JSON y CSV.

## Generación

```bash
docker compose run \
  --rm \
  --no-deps \
  --user "$(id -u):$(id -g)" \
  -v "$PWD:/workspace" \
  -w /workspace \
  backend \
  python scripts/generate_batch_20.py \
    --output samples/batch_20 \
    --batch-code L20A \
    --clean
```

## Carga y validación
```bash
python3 scripts/upload_verify_batch_20.py \
  --directory samples/batch_20 \
  --base-url http://localhost:8001 \
  --identifier admin \
  --password 'Admin123*'
```

Para verificar un lote ya cargado
```bash
python3 scripts/upload_verify_batch_20.py \
  --directory samples/batch_20 \
  --base-url http://localhost:8001 \
  --identifier admin \
  --password 'Admin123*' \
  --skip-upload
```

## Resultado obtenido

Las 20 facturas del lote terminaron en estado PROCESSED.

El sistema quedó con:

* 23 facturas procesadas.
* 1 factura duplicada.
* Confianza OCR entre 90.26% y 94.37%.