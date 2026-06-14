export const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000/api/v1";


export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}


export async function apiRequest(
  path,
  {
    method = "GET",
    token = null,
    body = undefined,
    headers = {},
  } = {}
) {
  const requestHeaders = {
    Accept: "application/json",
    ...headers,
  };

  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
  }

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers: requestHeaders,
      body:
        body !== undefined
          ? JSON.stringify(body)
          : undefined,
    });
  } catch {
    throw new ApiError(
      "No fue posible comunicarse con el servidor.",
      0
    );
  }

  let data = null;

  if (response.status !== 204) {
    const contentType =
      response.headers.get("content-type") ?? "";

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { detail: text } : null;
    }
  }

  if (!response.ok) {
    const detail =
      data?.detail ??
      `La solicitud terminó con estado ${response.status}.`;

    const message = Array.isArray(detail)
      ? detail
          .map((item) => item.msg ?? "Dato inválido")
          .join(". ")
      : detail;

    throw new ApiError(
      message,
      response.status,
      data
    );
  }

  return data;
}
