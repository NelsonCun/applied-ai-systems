import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export function obtenerDetalleError(error) {
  const detalle = error.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

  if (Array.isArray(detalle) && detalle.length > 0) {
    return detalle.map((item) => item.msg).join(" ");
  }

  if (error.code === "ECONNABORTED") {
    return "La operación excedió el tiempo de espera.";
  }

  if (error.request) {
    return "No se recibió respuesta del servidor.";
  }

  return "Ocurrió un error inesperado.";
}

export async function obtenerSintomas() {
  const response = await api.get("/api/sintomas");
  return response.data.sintomas;
}

export async function diagnosticarSintomas(sintomas) {
  const response = await api.post(
    "/api/diagnosticar",
    { sintomas },
    { timeout: 30000 },
  );

  return response.data;
}

export async function obtenerHistorial() {
  const response = await api.get("/api/historial");
  return response.data.historial;
}

export async function eliminarHistorial() {
  const response = await api.delete("/api/historial");
  return response.data;
}

export async function obtenerDatosAdministracion() {
  const [sintomas, fallas, recomendaciones, reglas, configuracion] =
    await Promise.all([
      api.get("/api/admin/sintomas"),
      api.get("/api/admin/fallas"),
      api.get("/api/admin/recomendaciones"),
      api.get("/api/admin/reglas"),
      api.get("/api/admin/configuracion/telegram"),
    ]);

  return {
    sintomas: sintomas.data.sintomas,
    fallas: fallas.data.fallas,
    recomendaciones: recomendaciones.data.recomendaciones,
    reglas: reglas.data.reglas,
    configuracion: configuracion.data,
  };
}

export async function crearSintoma(datos) {
  return (await api.post("/api/admin/sintomas", datos)).data;
}

export async function actualizarSintoma(id, datos) {
  return (await api.put(`/api/admin/sintomas/${id}`, datos)).data;
}

export async function eliminarSintoma(id) {
  return (await api.delete(`/api/admin/sintomas/${id}`)).data;
}

export async function crearFalla(datos) {
  return (await api.post("/api/admin/fallas", datos)).data;
}

export async function actualizarFalla(id, datos) {
  return (await api.put(`/api/admin/fallas/${id}`, datos)).data;
}

export async function eliminarFalla(id) {
  return (await api.delete(`/api/admin/fallas/${id}`)).data;
}

export async function crearRecomendacion(datos) {
  return (await api.post("/api/admin/recomendaciones", datos)).data;
}

export async function actualizarRecomendacion(id, datos) {
  return (await api.put(`/api/admin/recomendaciones/${id}`, datos)).data;
}

export async function eliminarRecomendacion(id) {
  return (await api.delete(`/api/admin/recomendaciones/${id}`)).data;
}

export async function crearRegla(datos) {
  return (await api.post("/api/admin/reglas", datos)).data;
}

export async function actualizarRegla(id, datos) {
  return (await api.put(`/api/admin/reglas/${id}`, datos)).data;
}

export async function eliminarRegla(id) {
  return (await api.delete(`/api/admin/reglas/${id}`)).data;
}

export async function actualizarConfiguracionTelegram(datos) {
  return (await api.put("/api/admin/configuracion/telegram", datos)).data;
}
