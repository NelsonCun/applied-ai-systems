import {
  FileCheck2,
  LoaderCircle,
  LockKeyhole,
  ScanText,
  ShieldCheck,
  UserRound,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import {
  getApiErrorMessage,
} from "../api/client";

import { useAuth } from "../context/AuthContext";


export default function LoginPage() {
  const navigate = useNavigate();

  const {
    login,
    loading,
    isAuthenticated,
  } = useAuth();

  const [identifier, setIdentifier] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [submitting, setSubmitting] =
    useState(false);


  useEffect(() => {
    setError("");
  }, [identifier, password]);


  if (
    !loading &&
    isAuthenticated
  ) {
    return <Navigate to="/" replace />;
  }


  async function handleSubmit(event) {
    event.preventDefault();

    if (
      !identifier.trim() ||
      !password
    ) {
      setError(
        "Ingrese su usuario y contraseña.",
      );

      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await login(
        identifier.trim(),
        password,
      );

      navigate("/", {
        replace: true,
      });
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "No fue posible iniciar sesión.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <div className="login-page">
      <section className="login-presentation">
        <div className="login-presentation-content">
          <div className="login-brand">
            <div className="login-brand-symbol">
              <ScanText size={32} />
            </div>

            <div>
              <strong>SmartInvoice</strong>
              <span>
                Procesamiento inteligente
                de facturas
              </span>
            </div>
          </div>

          <div className="login-hero">
            <p className="eyebrow">
              Administración documental
            </p>

            <h1>
              Transforme documentos en
              información útil.
            </h1>

            <p>
              Digitalización, OCR,
              validación, reportes y
              automatización desde una
              plataforma centralizada.
            </p>
          </div>

          <div className="login-features">
            <article>
              <FileCheck2 size={22} />

              <div>
                <strong>
                  Procesamiento automático
                </strong>

                <span>
                  Extracción y validación
                  mediante OCR.
                </span>
              </div>
            </article>

            <article>
              <ShieldCheck size={22} />

              <div>
                <strong>
                  Gestión controlada
                </strong>

                <span>
                  Historial, trazabilidad
                  y acceso protegido.
                </span>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section className="login-form-section">
        <form
          className="login-card"
          onSubmit={handleSubmit}
        >
          <header>
            <p className="eyebrow">
              Acceso administrativo
            </p>

            <h2>Iniciar sesión</h2>

            <p>
              Ingrese sus credenciales para
              continuar.
            </p>
          </header>

          <label className="form-field">
            <span>
              Usuario o correo electrónico
            </span>

            <div className="input-with-icon">
              <UserRound size={19} />

              <input
                type="text"
                value={identifier}
                autoComplete="username"
                placeholder="admin"
                onChange={(event) =>
                  setIdentifier(
                    event.target.value,
                  )
                }
              />
            </div>
          </label>

          <label className="form-field">
            <span>Contraseña</span>

            <div className="input-with-icon">
              <LockKeyhole size={19} />

              <input
                type="password"
                value={password}
                autoComplete="current-password"
                placeholder="••••••••"
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
              />
            </div>
          </label>

          {error && (
            <div
              className="form-alert form-alert-error"
              role="alert"
            >
              {error}
            </div>
          )}

          <button
            className="primary-button login-submit"
            type="submit"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <LoaderCircle
                  size={19}
                  className="spin"
                />

                Validando...
              </>
            ) : (
              "Ingresar"
            )}
          </button>

          <div className="login-test-credentials">
            <strong>
              Credenciales iniciales
            </strong>

            <span>
              Usuario: admin
            </span>

            <span>
              Contraseña: Admin123*
            </span>
          </div>
        </form>
      </section>
    </div>
  );
}
