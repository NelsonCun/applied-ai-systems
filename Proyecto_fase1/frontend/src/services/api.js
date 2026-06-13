import axios from "axios";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export async function obtenerSintomas() {
  const response = await api.get(
    "/api/sintomas"
  );

  return response.data.sintomas;
}

export async function diagnosticarSintomas(
  sintomas
) {
  const response = await api.post(
    "/api/diagnosticar",
    {
      sintomas,
    },
    {
      // El diagnóstico también consulta Prolog y Telegram.
      timeout: 30000,
    }
  );

  return response.data;
}

export async function obtenerHistorial() {
  const response = await api.get(
    "/api/historial"
  );

  return response.data.historial;
}

export async function eliminarHistorial() {
  const response = await api.delete(
    "/api/historial"
  );

  return response.data;
}