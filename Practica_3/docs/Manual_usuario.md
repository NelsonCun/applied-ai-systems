# Manual de usuario

## 1. Acceso

Abra:

```text
http://localhost:5174
```

Use las credenciales de desarrollo:

```text
Usuario: admin
Contraseña: Admin123*
```

## 2. Navegación

El menú contiene:

- Dashboard
- Proveedores
- Facturas
- Reportes
- Automatizaciones
- Correos

## 3. Dashboard

Muestra:

- total de facturas;
- pendientes y procesadas;
- rechazadas y duplicadas;
- monto e impuestos;
- confianza OCR promedio;
- distribución por estado;
- proveedores principales;
- comportamiento mensual.

## 4. Proveedores

### Crear

1. Abra **Proveedores**.
2. Presione **Nuevo proveedor**.
3. Complete nombre, NIT, correo, teléfono, dirección y categoría.
4. Guarde.

### Editar

1. Localice el proveedor.
2. Abra la acción de edición.
3. Modifique los datos.
4. Guarde.

### Desactivar

Utilice el control de estado. La desactivación es lógica y conserva el historial.

## 5. Facturas

### Carga individual

1. Abra **Facturas**.
2. Presione la opción de carga.
3. Seleccione PDF, JPG, JPEG o PNG.
4. Opcionalmente seleccione proveedor y categoría.
5. Confirme.
6. Espere la actualización automática.

### Carga masiva

1. Seleccione hasta 20 archivos.
2. Confirme la carga.
3. Revise el resumen de recibidos, correctos, duplicados y fallidos.
4. Espere a que finalice el worker.

### Estados

| Estado | Significado |
|---|---|
| Pendiente | Almacenada y en cola |
| Procesando | Worker ejecutando OCR |
| Procesada | Datos válidos |
| Rechazada | Requiere corrección |
| Error | Fallo técnico |
| Duplicada | Documento o factura ya registrada |

### Detalle

Desde la tabla puede:

- ver el archivo original;
- ver la imagen procesada;
- consultar texto OCR;
- revisar confianza;
- consultar campos;
- consultar bitácora;
- reprocesar;
- corregir.

### Revisión manual

1. Abra una factura rechazada.
2. Seleccione **Revisar**.
3. Corrija número, fecha, proveedor, categoría, NIT y montos.
4. Compruebe que subtotal + IVA = total.
5. Guarde.
6. La factura quedará procesada si supera las validaciones.

## 6. Reportes

1. Abra **Reportes**.
2. Presione **Nuevo reporte**.
3. Seleccione tipo.
4. Seleccione PDF, XLSX o CSV.
5. Configure filtros.
6. Genere.
7. Espere estado **Correcto**.
8. Descargue o envíe por correo.

## 7. Automatizaciones RPA

1. Abra **Automatizaciones**.
2. Presione **Nueva ejecución**.
3. Seleccione una factura procesada.
4. Ejecute.
5. Espere estado **Correcto**.
6. Abra el detalle.
7. Descargue la captura de evidencia.

## 8. Correos

1. Abra **Correos**.
2. Consulte destinatario, asunto, reporte y estado.
3. Abra el detalle para ver cuerpo y datos SMTP.
4. Descargue el adjunto.
5. Use **Abrir MailHog** para consultar el buzón de desarrollo.

## 9. Cerrar sesión

Presione **Cerrar sesión** al final del menú lateral.

## 10. Problemas frecuentes

### No se conecta al servidor

```bash
docker compose ps
curl -s http://localhost:8001/api/v1/health
```

### Una factura queda rechazada

Abra OCR y revise `validation_errors`. Luego use revisión manual.

### El reporte no descarga

Espere hasta que el estado sea `SUCCESS`.

### La RPA no inicia

Compruebe que la factura esté `PROCESSED` y que `rpa-target` esté saludable.

### El correo no aparece

Revise el estado y abra MailHog en `http://localhost:8025`.
