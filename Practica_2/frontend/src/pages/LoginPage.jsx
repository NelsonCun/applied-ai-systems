import { useState } from "react";

import { apiRequest } from "../api/client";
import { ErrorBox } from "../components/Ui";


function LoginPage({ onLogin }) {
  const [username, setUsername] =
    useState("IA1-User");

  const [password, setPassword] =
    useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] =
    useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      const data = await apiRequest(
        "/auth/login",
        {
          method: "POST",
          body: {
            username,
            password,
          },
        }
      );

      onLogin(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">
          <div className="brand-symbol brand-symbol-large">
            SB
          </div>

          <div>
            <p className="eyebrow">
              Administración segura
            </p>

            <h1>SmartBot Hospital</h1>
          </div>
        </div>

        <div className="login-copy">
          <h2>Iniciar sesión</h2>

          <p>
            Administre las preguntas frecuentes,
            respuestas, categorías y consultas
            recibidas desde Telegram.
          </p>
        </div>

        <ErrorBox message={error} />

        <form
          className="form-grid"
          onSubmit={handleSubmit}
        >
          <label className="field">
            <span>Usuario</span>

            <input
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              autoComplete="username"
              required
              maxLength={100}
            />
          </label>

          <label className="field">
            <span>Contraseña</span>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              autoComplete="current-password"
              required
              maxLength={200}
              autoFocus
            />
          </label>

          <button
            type="submit"
            className="btn btn-primary btn-large btn-full"
            disabled={submitting}
          >
            {submitting
              ? "Validando acceso..."
              : "Ingresar al panel"}
          </button>
        </form>

        <p className="login-footer">
          Hospital Vida Central · SmartBot
        </p>
      </section>

      <section className="login-visual">
        <div className="visual-content">
          <span className="visual-tag">
            Atención automatizada
          </span>

          <h2>
            Información hospitalaria clara,
            centralizada y disponible.
          </h2>

          <p>
            El panel permite mantener el
            conocimiento utilizado por el bot y
            revisar cada consulta realizada.
          </p>

          <div className="visual-features">
            <article>
              <strong>24/7</strong>
              <span>Disponibilidad del bot</span>
            </article>

            <article>
              <strong>REST</strong>
              <span>API centralizada</span>
            </article>

            <article>
              <strong>SQL</strong>
              <span>Persistencia confiable</span>
            </article>
          </div>
        </div>
      </section>
    </main>
  );
}


export default LoginPage;
