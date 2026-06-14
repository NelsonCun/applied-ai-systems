import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import {
  ErrorBox,
  LoadingState,
  StatusBadge,
} from "../components/Ui";


const EMPTY_FORM = {
  hospital_name: "",
  telegram_chat_id: "",
  bot_username: "",
  welcome_message: "",
  unknown_question_message: "",
  is_active: true,
};


function SettingsPage({
  token,
  notify,
}) {
  const [form, setForm] =
    useState(EMPTY_FORM);

  const [testMessage, setTestMessage] =
    useState(
      "Prueba de integración de SmartBot Hospital con Telegram."
    );

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [testing, setTesting] =
    useState(false);

  const [error, setError] = useState("");

  const loadSettings = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest(
        "/settings/telegram",
        { token }
      );

      setForm({
        hospital_name:
          data.hospital_name,
        telegram_chat_id:
          data.telegram_chat_id ?? "",
        bot_username:
          data.bot_username ?? "",
        welcome_message:
          data.welcome_message,
        unknown_question_message:
          data.unknown_question_message,
        is_active: data.is_active,
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, [token]);

  const saveSettings = async (event) => {
    event.preventDefault();

    setSaving(true);
    setError("");

    try {
      const data = await apiRequest(
        "/settings/telegram",
        {
          method: "PUT",
          token,
          body: {
            hospital_name:
              form.hospital_name,
            telegram_chat_id:
              form.telegram_chat_id.trim() ||
              null,
            bot_username:
              form.bot_username.trim() ||
              null,
            welcome_message:
              form.welcome_message,
            unknown_question_message:
              form.unknown_question_message,
            is_active: form.is_active,
          },
        }
      );

      setForm({
        hospital_name:
          data.hospital_name,
        telegram_chat_id:
          data.telegram_chat_id ?? "",
        bot_username:
          data.bot_username ?? "",
        welcome_message:
          data.welcome_message,
        unknown_question_message:
          data.unknown_question_message,
        is_active: data.is_active,
      });

      notify(
        "Configuración guardada correctamente."
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const sendTestMessage = async () => {
    setTesting(true);
    setError("");

    try {
      const result = await apiRequest(
        "/settings/telegram/test-message",
        {
          method: "POST",
          token,
          body: {
            message:
              testMessage.trim() || null,
          },
        }
      );

      notify(
        `${result.detail} ID del mensaje: ${result.message_id}.`
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <LoadingState message="Cargando la configuración..." />
    );
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>Configuración del bot</h2>

          <p>
            Defina la identidad, mensajes y chat
            utilizado por Telegram.
          </p>
        </div>

        <StatusBadge
          active={form.is_active}
          activeLabel="Bot activo"
          inactiveLabel="Bot desactivado"
        />
      </section>

      <ErrorBox message={error} />

      <form
        className="settings-grid"
        onSubmit={saveSettings}
      >
        <section className="panel">
          <header className="panel-header">
            <div>
              <h3>Información general</h3>

              <p>
                Datos visibles y mensajes enviados
                a los usuarios.
              </p>
            </div>
          </header>

          <div className="form-grid">
            <label className="field">
              <span>
                Nombre de la institución
              </span>

              <input
                type="text"
                value={form.hospital_name}
                onChange={(event) =>
                  setForm({
                    ...form,
                    hospital_name:
                      event.target.value,
                  })
                }
                minLength={2}
                maxLength={150}
                required
              />
            </label>

            <label className="field">
              <span>
                Mensaje de bienvenida
              </span>

              <textarea
                value={form.welcome_message}
                onChange={(event) =>
                  setForm({
                    ...form,
                    welcome_message:
                      event.target.value,
                  })
                }
                rows={5}
                minLength={2}
                maxLength={2000}
                required
              />
            </label>

            <label className="field">
              <span>
                Mensaje cuando no existe respuesta
              </span>

              <textarea
                value={
                  form.unknown_question_message
                }
                onChange={(event) =>
                  setForm({
                    ...form,
                    unknown_question_message:
                      event.target.value,
                  })
                }
                rows={5}
                minLength={2}
                maxLength={2000}
                required
              />
            </label>

            <label className="switch-field">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) =>
                  setForm({
                    ...form,
                    is_active:
                      event.target.checked,
                  })
                }
              />

              <span>
                Permitir que el bot responda consultas
              </span>
            </label>
          </div>
        </section>

        <div className="settings-column">
          <section className="panel">
            <header className="panel-header">
              <div>
                <h3>Telegram</h3>

                <p>
                  Identificación del bot y chat
                  configurado.
                </p>
              </div>
            </header>

            <div className="form-grid">
              <label className="field">
                <span>
                  ID del chat o grupo
                </span>

                <input
                  type="text"
                  value={
                    form.telegram_chat_id
                  }
                  onChange={(event) =>
                    setForm({
                      ...form,
                      telegram_chat_id:
                        event.target.value,
                    })
                  }
                  maxLength={100}
                  placeholder="Ejemplo: 1503184400"
                />
              </label>

              <label className="field">
                <span>
                  Usuario del bot
                </span>

                <input
                  type="text"
                  value={form.bot_username}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      bot_username:
                        event.target.value,
                    })
                  }
                  maxLength={100}
                  placeholder="nombre_del_bot"
                />
              </label>

              <div className="security-note">
                <strong>
                  Token protegido
                </strong>

                <p>
                  El token se administra mediante
                  variables de entorno y no se muestra
                  ni almacena desde este panel.
                </p>
              </div>
            </div>
          </section>

          <section className="panel">
            <header className="panel-header">
              <div>
                <h3>Mensaje de prueba</h3>

                <p>
                  Envíe un mensaje al chat configurado.
                </p>
              </div>
            </header>

            <div className="form-grid">
              <label className="field">
                <span>Mensaje</span>

                <textarea
                  value={testMessage}
                  onChange={(event) =>
                    setTestMessage(
                      event.target.value
                    )
                  }
                  rows={4}
                  maxLength={2000}
                />
              </label>

              <button
                type="button"
                className="btn btn-secondary btn-full"
                onClick={sendTestMessage}
                disabled={testing}
              >
                {testing
                  ? "Enviando..."
                  : "Enviar mensaje de prueba"}
              </button>
            </div>
          </section>
        </div>

        <footer className="settings-actions">
          <button
            type="submit"
            className="btn btn-primary btn-large"
            disabled={saving}
          >
            {saving
              ? "Guardando..."
              : "Guardar configuración"}
          </button>
        </footer>
      </form>
    </div>
  );
}


export default SettingsPage;
