import {
  ArrowRight,
  Check,
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
      <section className="login-visual-panel">
        <div className="login-visual-content">
          <div className="login-brand">
            <div className="login-brand-mark">
              <ScanText size={25} />
            </div>

            <div>
              <strong>SmartInvoice</strong>
              <span>
                Gestión inteligente de facturas
              </span>
            </div>
          </div>

          <div className="login-visual-heading">
            <span className="login-kicker">
              Administración documental
            </span>

            <h1>
              De una factura a información
              confiable.
            </h1>

            <p>
              Digitalice, valide y gestione
              documentos desde una plataforma
              centralizada.
            </p>
          </div>

          <div className="document-scene">
            <article className="document-card document-card-back">
              <div className="document-mini-header">
                <span>SMART</span>
                <strong>INVOICE</strong>
              </div>

              <div className="document-brush" />

              <div className="document-lines">
                <span />
                <span />
                <span />
              </div>

              <div className="document-circle-button">
                <ArrowRight size={20} />
              </div>
            </article>

            <article className="document-card document-card-front">
              <div className="invoice-preview-header">
                <div>
                  <span>Factura procesada</span>
                  <strong>FAC-2026-001</strong>
                </div>

                <div className="invoice-preview-icon">
                  <FileCheck2 size={22} />
                </div>
              </div>

              <div className="invoice-preview-row">
                <span>Proveedor</span>
                <strong>
                  Tecnología Maya, S.A.
                </strong>
              </div>

              <div className="invoice-preview-row">
                <span>NIT</span>
                <strong>1234567-8</strong>
              </div>

              <div className="invoice-preview-row">
                <span>Total</span>
                <strong>Q 1,120.00</strong>
              </div>

              <div className="invoice-preview-status">
                <Check size={16} />
                Validación completada
              </div>

              <div className="invoice-preview-brush" />
            </article>
          </div>

          <div className="login-visual-footer">
            <ShieldCheck size={18} />

            <span>
              Acceso seguro y trazabilidad
              completa.
            </span>
          </div>
        </div>
      </section>

      <section className="login-form-panel">
        <form
          className="login-card"
          onSubmit={handleSubmit}
        >
          <header className="login-card-header">
            <span className="section-kicker">
              Bienvenido
            </span>

            <h2>Iniciar sesión</h2>

            <p>
              Ingrese sus credenciales para
              acceder al panel administrativo.
            </p>
          </header>

          <label className="form-field">
            <span>
              Usuario o correo electrónico
            </span>

            <div className="input-with-icon">
              <UserRound size={18} />

              <input
                type="text"
                value={identifier}
                autoComplete="username"
                placeholder="Ingrese su usuario"
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
              <LockKeyhole size={18} />

              <input
                type="password"
                value={password}
                autoComplete="current-password"
                placeholder="Ingrese su contraseña"
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
            className="login-submit-button"
            type="submit"
            disabled={submitting}
          >
            <span>
              {submitting
                ? "Validando"
                : "Ingresar"}
            </span>

            <span className="login-submit-icon">
              {submitting ? (
                <LoaderCircle
                  size={18}
                  className="spin"
                />
              ) : (
                <ArrowRight size={18} />
              )}
            </span>
          </button>

        </form>
      </section>
    </div>
  );
}
