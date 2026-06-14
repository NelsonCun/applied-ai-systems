import { useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000/api/v1";

function App() {
  const [apiStatus, setApiStatus] = useState("Verificando");
  const [databaseStatus, setDatabaseStatus] = useState("Verificando");
  const [error, setError] = useState("");

  useEffect(() => {
    const verifyServices = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
          throw new Error(`La API respondió con estado ${response.status}`);
        }

        const data = await response.json();

        setApiStatus(data.status === "ok" ? "Disponible" : "No disponible");
        setDatabaseStatus(
          data.database === "connected"
            ? "Conectada"
            : "Sin conexión"
        );
      } catch (requestError) {
        setApiStatus("No disponible");
        setDatabaseStatus("No verificada");
        setError(requestError.message);
      }
    };

    verifyServices();
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <div className="brand">
          <div className="brand-mark">SB</div>

          <div>
            <p className="eyebrow">Sistema de atención automatizada</p>
            <h1>SmartBot Hospital</h1>
          </div>
        </div>

        <p className="description">
          Plataforma administrativa para gestionar preguntas frecuentes,
          respuestas, categorías y consultas recibidas desde Telegram.
        </p>
      </section>

      <section className="status-panel">
        <header>
          <p className="eyebrow">Diagnóstico inicial</p>
          <h2>Estado de los servicios</h2>
        </header>

        <div className="status-grid">
          <article className="status-card">
            <span>API REST</span>
            <strong>{apiStatus}</strong>
          </article>

          <article className="status-card">
            <span>PostgreSQL</span>
            <strong>{databaseStatus}</strong>
          </article>
        </div>

        {error && (
          <p className="error-message">
            Detalle: {error}
          </p>
        )}
      </section>
    </main>
  );
}

export default App;
