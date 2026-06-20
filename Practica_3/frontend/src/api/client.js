import axios from "axios";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8001/api/v1";

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(
      "smartinvoice_token",
    );

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes(
        "/auth/login",
      )
    ) {
      localStorage.removeItem(
        "smartinvoice_token",
      );

      localStorage.removeItem(
        "smartinvoice_user",
      );

      window.location.replace("/login");
    }

    return Promise.reject(error);
  },
);

export function getApiErrorMessage(
  error,
  fallback = "Ocurrió un error inesperado.",
) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map(
        (item) =>
          item.msg ||
          item.message ||
          "Dato inválido",
      )
      .join(". ");
  }

  if (error.code === "ECONNABORTED") {
    return (
      "El servidor tardó demasiado " +
      "en responder."
    );
  }

  if (!error.response) {
    return (
      "No fue posible establecer conexión " +
      "con el servidor."
    );
  }

  return fallback;
}

export default apiClient;
