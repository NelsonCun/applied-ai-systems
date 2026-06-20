import {
  BarChart3,
  CalendarDays,
  CheckCircle2,
  Download,
  Eye,
  FileBarChart,
  FileSpreadsheet,
  FileText,
  Filter,
  LoaderCircle,
  Mail,
  Plus,
  RefreshCw,
  Search,
  Send,
  TriangleAlert,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import apiClient, {
  getApiErrorMessage,
} from "../api/client";

import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";


const reportTypes = [
  {
    value: "ADMINISTRATIVE",
    label: "Administrativo",
    description:
      "Información general para control administrativo.",
  },
  {
    value: "INVOICE_DETAIL",
    label: "Detalle de facturas",
    description:
      "Listado detallado de documentos y montos.",
  },
  {
    value: "SUMMARY",
    label: "Resumen ejecutivo",
    description:
      "Indicadores consolidados del procesamiento.",
  },
  {
    value: "ERRORS",
    label: "Errores y excepciones",
    description:
      "Facturas rechazadas, duplicadas o con errores.",
  },
];


const reportFormats = [
  {
    value: "PDF",
    label: "PDF",
    description: "Documento listo para imprimir.",
  },
  {
    value: "XLSX",
    label: "Excel",
    description: "Libro de cálculo editable.",
  },
  {
    value: "CSV",
    label: "CSV",
    description: "Datos tabulares compatibles.",
  },
];


const invoiceStatuses = [
  {
    value: "",
    label: "Todos los estados",
  },
  {
    value: "PENDING",
    label: "Pendientes",
  },
  {
    value: "PROCESSING",
    label: "Procesando",
  },
  {
    value: "PROCESSED",
    label: "Procesadas",
  },
  {
    value: "REJECTED",
    label: "Rechazadas",
  },
  {
    value: "ERROR",
    label: "Con error",
  },
  {
    value: "DUPLICATE",
    label: "Duplicadas",
  },
];


const emptyReportForm = {
  report_type: "ADMINISTRATIVE",
  format: "PDF",
  date_from: "",
  date_to: "",
  provider_id: "",
  status: "",
};


const emptyEmailForm = {
  recipient: "",
  subject: "",
  message: "",
};


function normalizeCollection(
  value,
) {
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

  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}


function getReportTypeLabel(value) {
  return (
    reportTypes.find(
      (item) => item.value === value,
    )?.label || value
  );
}


function getReportIcon(format) {
  if (format === "XLSX") {
    return FileSpreadsheet;
  }

  if (format === "CSV") {
    return FileBarChart;
  }

  return FileText;
}


function getReportFileExtension(format) {
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


function describeFilters(
  report,
  providers,
) {
  const filters = report.filters || {};
  const descriptions = [];

  if (filters.date_from) {
    descriptions.push(
      `Desde ${filters.date_from}`,
    );
  }

  if (filters.date_to) {
    descriptions.push(
      `Hasta ${filters.date_to}`,
    );
  }

  if (filters.status) {
    const statusLabel =
      invoiceStatuses.find(
        (item) =>
          item.value === filters.status,
      )?.label || filters.status;

    descriptions.push(statusLabel);
  }

  if (filters.provider_id) {
    const provider = providers.find(
      (item) =>
        item.id ===
        Number(filters.provider_id),
    );

    descriptions.push(
      provider?.name ||
      `Proveedor #${filters.provider_id}`,
    );
  }

  return descriptions.length > 0
    ? descriptions.join(" · ")
    : "Sin filtros adicionales";
}


export default function ReportsPage() {
  const [reports, setReports] =
    useState([]);

  const [providers, setProviders] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [pageError, setPageError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("");

  const [generateOpen, setGenerateOpen] =
    useState(false);

  const [generating, setGenerating] =
    useState(false);

  const [generateError, setGenerateError] =
    useState("");

  const [reportForm, setReportForm] =
    useState(emptyReportForm);

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [
    selectedReport,
    setSelectedReport,
  ] = useState(null);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const [actionError, setActionError] =
    useState("");

  const [downloading, setDownloading] =
    useState(false);

  const [emailOpen, setEmailOpen] =
    useState(false);

  const [emailForm, setEmailForm] =
    useState(emptyEmailForm);

  const [emailError, setEmailError] =
    useState("");

  const [sendingEmail, setSendingEmail] =
    useState(false);


  const loadProviders =
    useCallback(async () => {
      try {
        const response =
          await apiClient.get(
            "/providers",
            {
              params: {
                page: 1,
                page_size: 100,
              },
            },
          );

        setProviders(
          normalizeCollection(
            response.data,
          ).filter(
            (provider) =>
              provider.is_active !== false,
          ),
        );
      } catch (requestError) {
        setPageError(
          getApiErrorMessage(
            requestError,
            "No fue posible cargar los proveedores.",
          ),
        );
      }
    }, []);


  const loadReports = useCallback(
    async ({
      silent = false,
    } = {}) => {
      if (!silent) {
        setLoading(true);
      }

      try {
        const response =
          await apiClient.get(
            "/reports",
            {
              params: {
                page: 1,
                page_size: 100,
              },
            },
          );

        setReports(
          normalizeCollection(
            response.data,
          ),
        );

        if (!silent) {
          setPageError("");
        }
      } catch (requestError) {
        if (!silent) {
          setPageError(
            getApiErrorMessage(
              requestError,
              "No fue posible cargar los reportes.",
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
    loadProviders();
    loadReports();
  }, [
    loadProviders,
    loadReports,
  ]);


  const hasActiveReports = useMemo(
    () =>
      reports.some((report) =>
        [
          "PENDING",
          "PROCESSING",
          "RUNNING",
        ].includes(report.status),
      ),
    [reports],
  );


  useEffect(() => {
    if (!hasActiveReports) {
      return undefined;
    }

    const intervalId =
      window.setInterval(
        () => {
          loadReports({
            silent: true,
          });
        },
        4000,
      );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [
    hasActiveReports,
    loadReports,
  ]);


  const filteredReports = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return reports.filter((report) => {
      const matchesStatus =
        !statusFilter ||
        report.status === statusFilter;

      const values = [
        report.id,
        report.report_type,
        getReportTypeLabel(
          report.report_type,
        ),
        report.format,
        report.file_name,
        report.generated_by_name,
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
          value.includes(
            normalizedSearch,
          ),
        );

      return (
        matchesStatus &&
        matchesSearch
      );
    });
  }, [
    reports,
    search,
    statusFilter,
  ]);


  const metrics = useMemo(() => {
    const successful = reports.filter(
      (report) =>
        report.status === "SUCCESS",
    ).length;

    const active = reports.filter(
      (report) =>
        [
          "PENDING",
          "PROCESSING",
          "RUNNING",
        ].includes(report.status),
    ).length;

    const errors = reports.filter(
      (report) =>
        report.status === "ERROR",
    ).length;

    const formats = new Set(
      reports
        .filter(
          (report) =>
            report.status === "SUCCESS",
        )
        .map(
          (report) =>
            report.format,
        ),
    ).size;

    return {
      total: reports.length,
      successful,
      active,
      errors,
      formats,
    };
  }, [reports]);


  function updateReportForm(
    field,
    value,
  ) {
    setReportForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  function openGenerateModal() {
    setReportForm(emptyReportForm);
    setGenerateError("");
    setGenerateOpen(true);
  }


  function closeGenerateModal() {
    if (generating) {
      return;
    }

    setGenerateOpen(false);
    setGenerateError("");
  }


  async function generateReport(event) {
    event.preventDefault();

    if (
      reportForm.date_from &&
      reportForm.date_to &&
      reportForm.date_from >
        reportForm.date_to
    ) {
      setGenerateError(
        "La fecha inicial no puede ser mayor que la fecha final.",
      );

      return;
    }

    setGenerating(true);
    setGenerateError("");
    setMessage("");

    const payload = {
      report_type:
        reportForm.report_type,

      format:
        reportForm.format,

      date_from:
        reportForm.date_from || null,

      date_to:
        reportForm.date_to || null,

      provider_id:
        reportForm.provider_id
          ? Number(
              reportForm.provider_id,
            )
          : null,

      status:
        reportForm.status || null,
    };

    try {
      const response =
        await apiClient.post(
          "/reports",
          payload,
        );

      setGenerateOpen(false);

      setMessage(
        response.data?.message ||
        "El reporte fue enviado a generación.",
      );

      await loadReports();

      window.setTimeout(
        () => {
          loadReports({
            silent: true,
          });
        },
        3000,
      );
    } catch (requestError) {
      setGenerateError(
        getApiErrorMessage(
          requestError,
          "No fue posible generar el reporte.",
        ),
      );
    } finally {
      setGenerating(false);
    }
  }


  async function openReportDetail(
    report,
  ) {
    setSelectedReport(report);
    setDetailOpen(true);
    setDetailLoading(true);
    setActionError("");

    try {
      const response =
        await apiClient.get(
          `/reports/${report.id}`,
        );

      setSelectedReport(
        response.data,
      );
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(
          requestError,
          "No fue posible consultar el reporte.",
        ),
      );
    } finally {
      setDetailLoading(false);
    }
  }


  function closeDetailModal() {
    if (
      downloading ||
      sendingEmail
    ) {
      return;
    }

    setDetailOpen(false);
    setSelectedReport(null);
    setActionError("");
  }


  async function downloadReport(
    report,
  ) {
    setDownloading(true);
    setActionError("");

    try {
      const response =
        await apiClient.get(
          `/reports/${report.id}/download`,
          {
            responseType: "blob",
          },
        );

      const objectUrl =
        URL.createObjectURL(
          response.data,
        );

      const anchor =
        document.createElement("a");

      anchor.href = objectUrl;

      anchor.download =
        report.file_name ||
        (
          `smartinvoice_report_${report.id}.` +
          getReportFileExtension(
            report.format,
          )
        );

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      window.setTimeout(
        () => {
          URL.revokeObjectURL(
            objectUrl,
          );
        },
        30000,
      );
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(
          requestError,
          "No fue posible descargar el reporte.",
        ),
      );
    } finally {
      setDownloading(false);
    }
  }


  function openEmailModal(report) {
    setSelectedReport(report);

    setEmailForm({
      recipient: "",
      subject:
        `SmartInvoice - ${getReportTypeLabel(
          report.report_type,
        )} #${report.id}`,

      message:
        "Se adjunta el reporte generado por SmartInvoice.",
    });

    setEmailError("");
    setEmailOpen(true);
  }


  function closeEmailModal() {
    if (sendingEmail) {
      return;
    }

    setEmailOpen(false);
    setEmailError("");
  }


  function updateEmailForm(
    field,
    value,
  ) {
    setEmailForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  async function sendReportEmail(
    event,
  ) {
    event.preventDefault();

    if (!selectedReport) {
      return;
    }

    setSendingEmail(true);
    setEmailError("");
    setMessage("");

    try {
      const response =
        await apiClient.post(
          `/emails/reports/${selectedReport.id}`,
          {
            recipient:
              emailForm.recipient.trim(),

            subject:
              emailForm.subject.trim() ||
              null,

            message:
              emailForm.message.trim() ||
              null,
          },
        );

      setEmailOpen(false);

      setMessage(
        response.data?.message ||
        "El correo fue enviado a la cola de entrega.",
      );
    } catch (requestError) {
      setEmailError(
        getApiErrorMessage(
          requestError,
          "No fue posible enviar el reporte.",
        ),
      );
    } finally {
      setSendingEmail(false);
    }
  }


  return (
    <div className="reports-page">
      <header className="page-header">
        <div>
          <span className="section-kicker">
            Inteligencia administrativa
          </span>

          <h1>Reportes</h1>

          <p>
            Genere documentos ejecutivos,
            descargue resultados y distribuya
            la información por correo.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={openGenerateModal}
        >
          <Plus size={18} />
          Generar reporte
        </button>
      </header>

      <section className="report-metric-grid">
        <article className="report-metric report-metric-blue">
          <BarChart3 size={21} />

          <div>
            <span>Total generado</span>
            <strong>{metrics.total}</strong>
          </div>
        </article>

        <article className="report-metric report-metric-green">
          <CheckCircle2 size={21} />

          <div>
            <span>Disponibles</span>
            <strong>
              {metrics.successful}
            </strong>
          </div>
        </article>

        <article className="report-metric report-metric-orange">
          <LoaderCircle
            size={21}
            className={
              metrics.active > 0
                ? "spin"
                : ""
            }
          />

          <div>
            <span>En proceso</span>
            <strong>{metrics.active}</strong>
          </div>
        </article>

        <article className="report-metric report-metric-violet">
          <FileSpreadsheet size={21} />

          <div>
            <span>Formatos utilizados</span>
            <strong>
              {metrics.formats}
            </strong>
          </div>
        </article>

        <article className="report-metric report-metric-red">
          <TriangleAlert size={21} />

          <div>
            <span>Con error</span>
            <strong>{metrics.errors}</strong>
          </div>
        </article>
      </section>

      {message && (
        <div className="form-alert form-alert-success">
          {message}
        </div>
      )}

      {pageError && (
        <div className="form-alert form-alert-error">
          {pageError}
        </div>
      )}

      <section className="content-card reports-table-card">
        <div className="table-toolbar">
          <div className="search-input">
            <Search size={18} />

            <input
              type="search"
              value={search}
              placeholder="Buscar por tipo, formato, archivo o usuario"
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
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

              <option value="PROCESSING">
                Procesando
              </option>

              <option value="SUCCESS">
                Disponibles
              </option>

              <option value="ERROR">
                Con error
              </option>
            </select>

            <button
              className="secondary-button"
              type="button"
              disabled={loading}
              onClick={() =>
                loadReports()
              }
            >
              <RefreshCw
                size={17}
                className={
                  loading
                    ? "spin"
                    : ""
                }
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

            <p>
              Cargando reportes...
            </p>
          </div>
        ) : (
          <>
            <div className="table-result-summary">
              <span>
                {filteredReports.length}
                {" "}
                resultado
                {filteredReports.length === 1
                  ? ""
                  : "s"}
              </span>

              {hasActiveReports && (
                <span className="live-processing-indicator">
                  <span />
                  Actualización automática activa
                </span>
              )}
            </div>

            {filteredReports.length === 0 ? (
              <div className="table-state">
                <FileBarChart size={38} />

                <h3>
                  No se encontraron reportes
                </h3>

                <p>
                  Genere un reporte o modifique
                  los filtros de búsqueda.
                </p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table report-table">
                  <thead>
                    <tr>
                      <th>Reporte</th>
                      <th>Formato</th>
                      <th>Filtros</th>
                      <th>Generado por</th>
                      <th>Fecha</th>
                      <th>Estado</th>
                      <th className="table-actions-column">
                        Acciones
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredReports.map(
                      (report) => {
                        const ReportIcon =
                          getReportIcon(
                            report.format,
                          );

                        return (
                          <tr key={report.id}>
                            <td>
                              <div className="table-primary-cell">
                                <div
                                  className={[
                                    "table-avatar",
                                    "report-format-avatar",
                                    `report-format-${report.format.toLowerCase()}`,
                                  ].join(" ")}
                                >
                                  <ReportIcon
                                    size={18}
                                  />
                                </div>

                                <div>
                                  <strong>
                                    {getReportTypeLabel(
                                      report.report_type,
                                    )}
                                  </strong>

                                  <span>
                                    {report.file_name ||
                                      `Reporte #${report.id}`}
                                  </span>
                                </div>
                              </div>
                            </td>

                            <td>
                              <span
                                className={[
                                  "report-format-badge",
                                  `report-format-badge-${report.format.toLowerCase()}`,
                                ].join(" ")}
                              >
                                {report.format}
                              </span>
                            </td>

                            <td>
                              <span className="report-filter-summary">
                                {describeFilters(
                                  report,
                                  providers,
                                )}
                              </span>
                            </td>

                            <td>
                              <div className="stacked-value">
                                <span>
                                  {report.generated_by_name ||
                                    "Usuario no disponible"}
                                </span>

                                <small>
                                  ID:
                                  {" "}
                                  {report.generated_by ||
                                    "—"}
                                </small>
                              </div>
                            </td>

                            <td>
                              {formatDateTime(
                                report.generated_at ||
                                report.created_at,
                              )}
                            </td>

                            <td>
                              <StatusBadge
                                status={
                                  report.status
                                }
                              />
                            </td>

                            <td>
                              <div className="row-actions">
                                <button
                                  className="table-icon-button"
                                  type="button"
                                  title="Consultar reporte"
                                  onClick={() =>
                                    openReportDetail(
                                      report,
                                    )
                                  }
                                >
                                  <Eye size={17} />
                                </button>

                                <button
                                  className="table-icon-button"
                                  type="button"
                                  title="Descargar reporte"
                                  disabled={
                                    report.status !==
                                      "SUCCESS" ||
                                    downloading
                                  }
                                  onClick={() =>
                                    downloadReport(
                                      report,
                                    )
                                  }
                                >
                                  <Download
                                    size={17}
                                  />
                                </button>

                                <button
                                  className="table-icon-button table-icon-button-mail"
                                  type="button"
                                  title="Enviar por correo"
                                  disabled={
                                    report.status !==
                                    "SUCCESS"
                                  }
                                  onClick={() =>
                                    openEmailModal(
                                      report,
                                    )
                                  }
                                >
                                  <Mail size={17} />
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      },
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>

      <Modal
        open={generateOpen}
        title="Generar reporte"
        subtitle="Configure el contenido, formato y filtros del documento."
        onClose={closeGenerateModal}
      >
        <form
          className="modal-form"
          onSubmit={generateReport}
        >
          <section className="report-type-selector">
            <span className="form-section-label">
              Tipo de reporte
            </span>

            <div>
              {reportTypes.map(
                (type) => (
                  <button
                    key={type.value}
                    type="button"
                    className={
                      reportForm.report_type ===
                      type.value
                        ? "report-option-active"
                        : ""
                    }
                    onClick={() =>
                      updateReportForm(
                        "report_type",
                        type.value,
                      )
                    }
                  >
                    <strong>
                      {type.label}
                    </strong>

                    <span>
                      {type.description}
                    </span>
                  </button>
                ),
              )}
            </div>
          </section>

          <section className="report-format-selector">
            <span className="form-section-label">
              Formato de salida
            </span>

            <div>
              {reportFormats.map(
                (format) => {
                  const FormatIcon =
                    getReportIcon(
                      format.value,
                    );

                  return (
                    <button
                      key={format.value}
                      type="button"
                      className={
                        reportForm.format ===
                        format.value
                          ? "report-option-active"
                          : ""
                      }
                      onClick={() =>
                        updateReportForm(
                          "format",
                          format.value,
                        )
                      }
                    >
                      <FormatIcon
                        size={20}
                      />

                      <strong>
                        {format.label}
                      </strong>

                      <span>
                        {format.description}
                      </span>
                    </button>
                  );
                },
              )}
            </div>
          </section>

          <div className="report-filter-box">
            <header>
              <Filter size={17} />

              <div>
                <strong>
                  Filtros opcionales
                </strong>

                <span>
                  El reporte incluirá todos los
                  registros cuando no seleccione
                  filtros.
                </span>
              </div>
            </header>

            <div className="form-grid">
              <label className="form-field">
                <span>Fecha inicial</span>

                <input
                  className="text-control"
                  type="date"
                  value={
                    reportForm.date_from
                  }
                  onChange={(event) =>
                    updateReportForm(
                      "date_from",
                      event.target.value,
                    )
                  }
                />
              </label>

              <label className="form-field">
                <span>Fecha final</span>

                <input
                  className="text-control"
                  type="date"
                  value={
                    reportForm.date_to
                  }
                  onChange={(event) =>
                    updateReportForm(
                      "date_to",
                      event.target.value,
                    )
                  }
                />
              </label>

              <label className="form-field">
                <span>Proveedor</span>

                <select
                  className="select-control"
                  value={
                    reportForm.provider_id
                  }
                  onChange={(event) =>
                    updateReportForm(
                      "provider_id",
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Todos los proveedores
                  </option>

                  {providers.map(
                    (provider) => (
                      <option
                        key={provider.id}
                        value={provider.id}
                      >
                        {provider.name}
                      </option>
                    ),
                  )}
                </select>
              </label>

              <label className="form-field">
                <span>
                  Estado de factura
                </span>

                <select
                  className="select-control"
                  value={
                    reportForm.status
                  }
                  onChange={(event) =>
                    updateReportForm(
                      "status",
                      event.target.value,
                    )
                  }
                >
                  {invoiceStatuses.map(
                    (status) => (
                      <option
                        key={
                          status.value ||
                          "ALL"
                        }
                        value={status.value}
                      >
                        {status.label}
                      </option>
                    ),
                  )}
                </select>
              </label>
            </div>
          </div>

          {generateError && (
            <div className="form-alert form-alert-error">
              {generateError}
            </div>
          )}

          <footer className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              disabled={generating}
              onClick={closeGenerateModal}
            >
              Cancelar
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={generating}
            >
              {generating ? (
                <LoaderCircle
                  className="spin"
                  size={17}
                />
              ) : (
                <BarChart3 size={17} />
              )}

              Generar reporte
            </button>
          </footer>
        </form>
      </Modal>

      <Modal
        open={detailOpen}
        title={
          selectedReport
            ? `${getReportTypeLabel(
                selectedReport.report_type,
              )} #${selectedReport.id}`
            : "Detalle del reporte"
        }
        subtitle={
          selectedReport?.file_name ||
          "Información del proceso de generación"
        }
        onClose={closeDetailModal}
      >
        {detailLoading ? (
          <div className="table-state report-detail-loading">
            <LoaderCircle
              className="spin"
              size={29}
            />

            <p>
              Consultando reporte...
            </p>
          </div>
        ) : selectedReport ? (
          <div className="report-detail">
            {actionError && (
              <div className="form-alert form-alert-error">
                {actionError}
              </div>
            )}

            <section className="report-detail-hero">
              <div>
                <span>
                  Reporte
                  {" "}
                  {selectedReport.format}
                </span>

                <strong>
                  {getReportTypeLabel(
                    selectedReport.report_type,
                  )}
                </strong>

                <small>
                  {selectedReport.file_name ||
                    "Archivo pendiente de generación"}
                </small>
              </div>

              <StatusBadge
                status={
                  selectedReport.status
                }
              />
            </section>

            <div className="report-detail-grid">
              <article>
                <CalendarDays size={18} />

                <div>
                  <span>Solicitado</span>

                  <strong>
                    {formatDateTime(
                      selectedReport.created_at,
                    )}
                  </strong>
                </div>
              </article>

              <article>
                <CheckCircle2 size={18} />

                <div>
                  <span>Generado</span>

                  <strong>
                    {formatDateTime(
                      selectedReport.generated_at,
                    )}
                  </strong>
                </div>
              </article>

              <article>
                <FileText size={18} />

                <div>
                  <span>Formato</span>

                  <strong>
                    {selectedReport.format}
                  </strong>
                </div>
              </article>

              <article>
                <Filter size={18} />

                <div>
                  <span>Filtros</span>

                  <strong>
                    {describeFilters(
                      selectedReport,
                      providers,
                    )}
                  </strong>
                </div>
              </article>
            </div>

            {selectedReport.error_message && (
              <div className="form-alert form-alert-error">
                {selectedReport.error_message}
              </div>
            )}

            <footer className="report-detail-actions">
              <button
                className="secondary-button"
                type="button"
                disabled={
                  selectedReport.status !==
                    "SUCCESS" ||
                  downloading
                }
                onClick={() =>
                  downloadReport(
                    selectedReport,
                  )
                }
              >
                {downloading ? (
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />
                ) : (
                  <Download size={17} />
                )}

                Descargar
              </button>

              <button
                className="primary-button"
                type="button"
                disabled={
                  selectedReport.status !==
                  "SUCCESS"
                }
                onClick={() =>
                  openEmailModal(
                    selectedReport,
                  )
                }
              >
                <Mail size={17} />
                Enviar por correo
              </button>
            </footer>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={emailOpen}
        title="Enviar reporte por correo"
        subtitle={
          selectedReport
            ? `${selectedReport.file_name || "Reporte"}`
            : "Adjuntar reporte"
        }
        onClose={closeEmailModal}
      >
        <form
          className="modal-form"
          onSubmit={sendReportEmail}
        >
          <label className="form-field">
            <span>
              Correo del destinatario
            </span>

            <input
              className="text-control"
              type="email"
              required
              value={
                emailForm.recipient
              }
              placeholder="usuario@empresa.com"
              onChange={(event) =>
                updateEmailForm(
                  "recipient",
                  event.target.value,
                )
              }
            />
          </label>

          <label className="form-field">
            <span>Asunto</span>

            <input
              className="text-control"
              minLength={3}
              maxLength={255}
              value={emailForm.subject}
              onChange={(event) =>
                updateEmailForm(
                  "subject",
                  event.target.value,
                )
              }
            />
          </label>

          <label className="form-field">
            <span>Mensaje</span>

            <textarea
              className="textarea-control"
              rows={6}
              minLength={3}
              maxLength={5000}
              value={emailForm.message}
              onChange={(event) =>
                updateEmailForm(
                  "message",
                  event.target.value,
                )
              }
            />
          </label>

          {emailError && (
            <div className="form-alert form-alert-error">
              {emailError}
            </div>
          )}

          <footer className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              disabled={sendingEmail}
              onClick={closeEmailModal}
            >
              Cancelar
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={sendingEmail}
            >
              {sendingEmail ? (
                <LoaderCircle
                  className="spin"
                  size={17}
                />
              ) : (
                <Send size={17} />
              )}

              Enviar reporte
            </button>
          </footer>
        </form>
      </Modal>
    </div>
  );
}
