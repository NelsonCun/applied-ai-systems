import {
  CheckCircle2,
  Clock3,
  Download,
  ExternalLink,
  Eye,
  FileText,
  Inbox,
  LoaderCircle,
  Mail,
  MailOpen,
  Paperclip,
  RefreshCw,
  Search,
  Send,
  Server,
  TriangleAlert,
  UserRound,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useNavigate } from "react-router-dom";

import apiClient, {
  getApiErrorMessage,
} from "../api/client";

import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";


const ACTIVE_STATUSES = [
  "PENDING",
  "PROCESSING",
  "SENDING",
  "QUEUED",
];

const REPORT_TYPE_LABELS = {
  ADMINISTRATIVE: "Administrativo",
  INVOICE_DETAIL: "Detalle de facturas",
  SUMMARY: "Resumen ejecutivo",
  ERRORS: "Errores y excepciones",
};


function normalizeCollection(value) {
  if (Array.isArray(value)) {
    return value;
  }

  if (Array.isArray(value?.items)) {
    return value.items;
  }

  return [];
}


function formatDateTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat("es-GT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}


function formatDuration(startedAt, finishedAt) {
  if (!startedAt) {
    return "No iniciado";
  }

  if (!finishedAt) {
    return "En proceso";
  }

  const started = new Date(startedAt);
  const finished = new Date(finishedAt);

  if (
    Number.isNaN(started.getTime()) ||
    Number.isNaN(finished.getTime())
  ) {
    return "—";
  }

  const milliseconds =
    finished.getTime() - started.getTime();

  if (milliseconds < 1000) {
    return `${milliseconds} ms`;
  }

  return `${(milliseconds / 1000).toFixed(2)} s`;
}


function getReportTypeLabel(value) {
  return (
    REPORT_TYPE_LABELS[value] ||
    value ||
    "Reporte"
  );
}


function getReportExtension(format) {
  const extensions = {
    PDF: "pdf",
    XLSX: "xlsx",
    CSV: "csv",
  };

  return (
    extensions[format] ||
    String(format || "file").toLowerCase()
  );
}


function getRecipientInitial(email) {
  return String(email || "?")
    .trim()
    .charAt(0)
    .toUpperCase();
}


export default function EmailsPage() {
  const navigate = useNavigate();

  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState("");

  const [detailOpen, setDetailOpen] =
    useState(false);
  const [selectedEmail, setSelectedEmail] =
    useState(null);
  const [detailLoading, setDetailLoading] =
    useState(false);
  const [actionError, setActionError] =
    useState("");
  const [
    downloadingAttachment,
    setDownloadingAttachment,
  ] = useState(false);

  const mailHogUrl =
    import.meta.env.VITE_MAILHOG_URL ||
    "http://localhost:8025";


  const loadEmails = useCallback(
    async ({ silent = false } = {}) => {
      if (!silent) {
        setLoading(true);
      }

      try {
        const response = await apiClient.get(
          "/emails",
          {
            params: {
              page: 1,
              page_size: 100,
            },
          },
        );

        setEmails(
          normalizeCollection(response.data),
        );

        if (!silent) {
          setPageError("");
        }
      } catch (requestError) {
        if (!silent) {
          setPageError(
            getApiErrorMessage(
              requestError,
              "No fue posible cargar el historial de correos.",
            ),
          );
        }
      } finally {
        if (!silent) {
          setLoading(false);
        }
      }
    },
    [],
  );


  useEffect(() => {
    loadEmails();
  }, [loadEmails]);


  const hasActiveEmails = useMemo(
    () =>
      emails.some((email) =>
        ACTIVE_STATUSES.includes(email.status),
      ),
    [emails],
  );


  useEffect(() => {
    if (!hasActiveEmails) {
      return undefined;
    }

    const intervalId = window.setInterval(
      () => {
        loadEmails({ silent: true });
      },
      3000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [hasActiveEmails, loadEmails]);


  const filteredEmails = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return emails.filter((email) => {
      const matchesStatus =
        !statusFilter ||
        email.status === statusFilter;

      const values = [
        email.id,
        email.report_id,
        email.report_type,
        email.report_format,
        email.report_file_name,
        email.recipient_email,
        email.subject,
        email.requested_by_name,
        email.attachment_name,
        email.smtp_message_id,
      ]
        .filter(
          (value) =>
            value !== null &&
            value !== undefined,
        )
        .map((value) =>
          String(value).toLowerCase(),
        );

      const matchesSearch =
        !normalizedSearch ||
        values.some((value) =>
          value.includes(normalizedSearch),
        );

      return matchesStatus && matchesSearch;
    });
  }, [emails, search, statusFilter]);


  const metrics = useMemo(() => {
    const successful = emails.filter(
      (email) => email.status === "SUCCESS",
    ).length;

    const active = emails.filter((email) =>
      ACTIVE_STATUSES.includes(email.status),
    ).length;

    const failed = emails.filter((email) =>
      ["ERROR", "FAILED"].includes(
        email.status,
      ),
    ).length;

    const withAttachment = emails.filter(
      (email) =>
        Boolean(
          email.attachment_name ||
          email.report_file_name,
        ),
    ).length;

    return {
      total: emails.length,
      successful,
      active,
      failed,
      withAttachment,
    };
  }, [emails]);


  async function openEmailDetail(email) {
    setSelectedEmail(email);
    setDetailOpen(true);
    setDetailLoading(true);
    setActionError("");

    try {
      const response = await apiClient.get(
        `/emails/${email.id}`,
      );

      setSelectedEmail(response.data);
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(
          requestError,
          "No fue posible consultar el correo.",
        ),
      );
    } finally {
      setDetailLoading(false);
    }
  }


  function closeDetailModal() {
    if (downloadingAttachment) {
      return;
    }

    setDetailOpen(false);
    setSelectedEmail(null);
    setActionError("");
  }


  async function downloadAttachment(email) {
    if (!email?.report_id) {
      setActionError(
        "El correo no posee un reporte relacionado.",
      );
      return;
    }

    setDownloadingAttachment(true);
    setActionError("");

    try {
      const response = await apiClient.get(
        `/reports/${email.report_id}/download`,
        {
          responseType: "blob",
        },
      );

      const objectUrl = URL.createObjectURL(
        response.data,
      );

      const anchor =
        document.createElement("a");

      anchor.href = objectUrl;
      anchor.download =
        email.attachment_name ||
        email.report_file_name ||
        (
          `smartinvoice_report_${email.report_id}.` +
          getReportExtension(
            email.report_format,
          )
        );

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      window.setTimeout(() => {
        URL.revokeObjectURL(objectUrl);
      }, 30000);
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(
          requestError,
          "No fue posible descargar el archivo adjunto.",
        ),
      );
    } finally {
      setDownloadingAttachment(false);
    }
  }


  function openMailHog() {
    window.open(
      mailHogUrl,
      "_blank",
      "noopener,noreferrer",
    );
  }


  return (
    <div className="emails-page">
      <header className="page-header">
        <div>
          <span className="section-kicker">
            Comunicación automatizada
          </span>

          <h1>Historial de correos</h1>

          <p>
            Consulte destinatarios, reportes,
            archivos adjuntos y resultados de
            entrega SMTP.
          </p>
        </div>

        <div className="page-header-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={openMailHog}
          >
            <ExternalLink size={17} />
            Abrir MailHog
          </button>

          <button
            className="primary-button"
            type="button"
            onClick={() => navigate("/reports")}
          >
            <Send size={18} />
            Enviar reporte
          </button>
        </div>
      </header>

      <section className="email-metric-grid">
        <article className="email-metric email-metric-blue">
          <Inbox size={21} />
          <div>
            <span>Total de correos</span>
            <strong>{metrics.total}</strong>
          </div>
        </article>

        <article className="email-metric email-metric-green">
          <CheckCircle2 size={21} />
          <div>
            <span>Entregados</span>
            <strong>{metrics.successful}</strong>
          </div>
        </article>

        <article className="email-metric email-metric-orange">
          <Clock3
            size={21}
            className={
              metrics.active > 0 ? "spin" : ""
            }
          />
          <div>
            <span>En proceso</span>
            <strong>{metrics.active}</strong>
          </div>
        </article>

        <article className="email-metric email-metric-violet">
          <Paperclip size={21} />
          <div>
            <span>Con adjunto</span>
            <strong>{metrics.withAttachment}</strong>
          </div>
        </article>

        <article className="email-metric email-metric-red">
          <TriangleAlert size={21} />
          <div>
            <span>Fallidos</span>
            <strong>{metrics.failed}</strong>
          </div>
        </article>
      </section>

      {pageError && (
        <div className="form-alert form-alert-error">
          {pageError}
        </div>
      )}

      <section className="content-card emails-table-card">
        <div className="table-toolbar">
          <div className="search-input">
            <Search size={18} />
            <input
              type="search"
              value={search}
              placeholder="Buscar destinatario, asunto, reporte o usuario"
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </div>

          <div className="toolbar-actions">
            <select
              className="select-control toolbar-select"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value,
                )
              }
            >
              <option value="">
                Todos los estados
              </option>
              <option value="PENDING">
                Pendientes
              </option>
              <option value="SENDING">
                Enviando
              </option>
              <option value="SUCCESS">
                Entregados
              </option>
              <option value="ERROR">
                Con error
              </option>
            </select>

            <button
              className="secondary-button"
              type="button"
              disabled={loading}
              onClick={() => loadEmails()}
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
              Actualizar
            </button>
          </div>
        </div>

        {loading ? (
          <div className="table-state">
            <LoaderCircle
              className="spin"
              size={30}
            />
            <p>Cargando correos...</p>
          </div>
        ) : (
          <>
            <div className="table-result-summary">
              <span>
                {filteredEmails.length} resultado
                {filteredEmails.length === 1
                  ? ""
                  : "s"}
              </span>

              {hasActiveEmails && (
                <span className="live-processing-indicator">
                  <span />
                  Actualización automática activa
                </span>
              )}
            </div>

            {filteredEmails.length === 0 ? (
              <div className="table-state">
                <MailOpen size={39} />
                <h3>
                  No existen correos registrados
                </h3>
                <p>
                  Envíe un reporte o modifique
                  los filtros de búsqueda.
                </p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table email-table">
                  <thead>
                    <tr>
                      <th>Destinatario</th>
                      <th>Asunto</th>
                      <th>Reporte</th>
                      <th>Solicitado por</th>
                      <th>Fecha</th>
                      <th>Estado</th>
                      <th className="table-actions-column">
                        Acciones
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredEmails.map(
                      (email) => (
                        <tr key={email.id}>
                          <td>
                            <div className="table-primary-cell">
                              <div className="table-avatar email-recipient-avatar">
                                {getRecipientInitial(
                                  email.recipient_email,
                                )}
                              </div>

                              <div>
                                <strong>
                                  {email.recipient_email}
                                </strong>
                                <span>
                                  Envío #{email.id}
                                </span>
                              </div>
                            </div>
                          </td>

                          <td>
                            <div className="email-subject-cell">
                              <strong>
                                {email.subject}
                              </strong>
                              <span>
                                {email.body}
                              </span>
                            </div>
                          </td>

                          <td>
                            <div className="stacked-value">
                              <span>
                                {getReportTypeLabel(
                                  email.report_type,
                                )}
                              </span>
                              <small>
                                {email.report_format ||
                                  "—"}
                                {" · "}
                                Reporte #
                                {email.report_id}
                              </small>
                            </div>
                          </td>

                          <td>
                            <div className="stacked-value">
                              <span>
                                {email.requested_by_name ||
                                  "Usuario no disponible"}
                              </span>
                              <small>
                                ID:{" "}
                                {email.requested_by ||
                                  "—"}
                              </small>
                            </div>
                          </td>

                          <td>
                            {formatDateTime(
                              email.sent_at ||
                              email.created_at,
                            )}
                          </td>

                          <td>
                            <StatusBadge
                              status={email.status}
                            />
                          </td>

                          <td>
                            <div className="row-actions">
                              <button
                                className="table-icon-button"
                                type="button"
                                title="Consultar correo"
                                onClick={() =>
                                  openEmailDetail(
                                    email,
                                  )
                                }
                              >
                                <Eye size={17} />
                              </button>

                              <button
                                className="table-icon-button email-download-button"
                                type="button"
                                title="Descargar adjunto"
                                disabled={
                                  !email.report_id ||
                                  downloadingAttachment
                                }
                                onClick={() =>
                                  downloadAttachment(
                                    email,
                                  )
                                }
                              >
                                <Download size={17} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>

      <Modal
        open={detailOpen}
        title={
          selectedEmail
            ? `Correo #${selectedEmail.id}`
            : "Detalle del correo"
        }
        subtitle={
          selectedEmail?.recipient_email ||
          "Información del envío"
        }
        size="large"
        onClose={closeDetailModal}
      >
        {detailLoading ? (
          <div className="table-state email-detail-loader">
            <LoaderCircle
              className="spin"
              size={30}
            />
            <p>Consultando correo...</p>
          </div>
        ) : selectedEmail ? (
          <div className="email-detail">
            {actionError && (
              <div className="form-alert form-alert-error">
                {actionError}
              </div>
            )}

            <section className="email-detail-hero">
              <div className="email-detail-title">
                <div>
                  <Mail size={25} />
                </div>

                <div>
                  <span>Destinatario</span>
                  <strong>
                    {selectedEmail.recipient_email}
                  </strong>
                  <small>
                    {selectedEmail.subject}
                  </small>
                </div>
              </div>

              <StatusBadge
                status={selectedEmail.status}
              />
            </section>

            <section className="email-detail-grid">
              <article>
                <UserRound size={18} />
                <div>
                  <span>Solicitado por</span>
                  <strong>
                    {selectedEmail
                      .requested_by_name ||
                      "Usuario no disponible"}
                  </strong>
                </div>
              </article>

              <article>
                <FileText size={18} />
                <div>
                  <span>Reporte</span>
                  <strong>
                    {getReportTypeLabel(
                      selectedEmail.report_type,
                    )}
                    {" · "}
                    {selectedEmail.report_format}
                  </strong>
                </div>
              </article>

              <article>
                <Clock3 size={18} />
                <div>
                  <span>Tiempo de entrega</span>
                  <strong>
                    {formatDuration(
                      selectedEmail.started_at,
                      selectedEmail.sent_at,
                    )}
                  </strong>
                </div>
              </article>

              <article>
                <CheckCircle2 size={18} />
                <div>
                  <span>Enviado</span>
                  <strong>
                    {formatDateTime(
                      selectedEmail.sent_at,
                    )}
                  </strong>
                </div>
              </article>
            </section>

            <section className="email-message-panel">
              <header>
                <MailOpen size={18} />
                <div>
                  <span>Asunto</span>
                  <strong>
                    {selectedEmail.subject}
                  </strong>
                </div>
              </header>

              <pre>{selectedEmail.body}</pre>
            </section>

            <section className="email-attachment-panel">
              <div className="email-attachment-icon">
                <Paperclip size={21} />
              </div>

              <div>
                <span>Archivo adjunto</span>
                <strong>
                  {selectedEmail.attachment_name ||
                    selectedEmail
                      .report_file_name ||
                    "Sin archivo adjunto"}
                </strong>
                <small>
                  Reporte #{selectedEmail.report_id}
                  {" · "}
                  {selectedEmail.report_format ||
                    "Formato no disponible"}
                </small>
              </div>

              <button
                className="secondary-button"
                type="button"
                disabled={
                  !selectedEmail.report_id ||
                  downloadingAttachment
                }
                onClick={() =>
                  downloadAttachment(
                    selectedEmail,
                  )
                }
              >
                {downloadingAttachment ? (
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />
                ) : (
                  <Download size={17} />
                )}
                Descargar
              </button>
            </section>

            <section className="email-smtp-panel">
              <header>
                <Server size={18} />
                <strong>
                  Información técnica SMTP
                </strong>
              </header>

              <dl>
                <div>
                  <dt>
                    Identificador del mensaje
                  </dt>
                  <dd>
                    {selectedEmail
                      .smtp_message_id ||
                      "No disponible"}
                  </dd>
                </div>

                <div>
                  <dt>Inicio del envío</dt>
                  <dd>
                    {formatDateTime(
                      selectedEmail.started_at,
                    )}
                  </dd>
                </div>

                <div>
                  <dt>Fecha de creación</dt>
                  <dd>
                    {formatDateTime(
                      selectedEmail.created_at,
                    )}
                  </dd>
                </div>

                <div>
                  <dt>
                    Última actualización
                  </dt>
                  <dd>
                    {formatDateTime(
                      selectedEmail.updated_at,
                    )}
                  </dd>
                </div>
              </dl>
            </section>

            {selectedEmail.error_message && (
              <div className="form-alert form-alert-error">
                {selectedEmail.error_message}
              </div>
            )}

            <footer className="email-detail-actions">
              <button
                className="secondary-button"
                type="button"
                onClick={openMailHog}
              >
                <ExternalLink size={17} />
                Ver en MailHog
              </button>

              <button
                className="primary-button"
                type="button"
                disabled={
                  !selectedEmail.report_id ||
                  downloadingAttachment
                }
                onClick={() =>
                  downloadAttachment(
                    selectedEmail,
                  )
                }
              >
                {downloadingAttachment ? (
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />
                ) : (
                  <Download size={17} />
                )}
                Descargar adjunto
              </button>
            </footer>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
