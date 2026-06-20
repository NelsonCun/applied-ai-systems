import {
  Activity,
  Bot,
  CheckCircle2,
  Clock3,
  Download,
  Eye,
  FileText,
  Image,
  LoaderCircle,
  Play,
  RefreshCw,
  Search,
  Server,
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


const activeStatuses = [
  "PENDING",
  "PROCESSING",
  "RUNNING",
];


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

  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}


function formatDuration(
  startedAt,
  finishedAt,
) {
  if (!startedAt) {
    return "No iniciada";
  }

  if (!finishedAt) {
    return "En ejecución";
  }

  const start = new Date(startedAt);
  const finish = new Date(finishedAt);

  if (
    Number.isNaN(start.getTime()) ||
    Number.isNaN(finish.getTime())
  ) {
    return "—";
  }

  const milliseconds =
    finish.getTime() -
    start.getTime();

  if (milliseconds < 1000) {
    return `${milliseconds} ms`;
  }

  if (milliseconds < 60000) {
    return `${(
      milliseconds / 1000
    ).toFixed(2)} s`;
  }

  const minutes = Math.floor(
    milliseconds / 60000,
  );

  const seconds = Math.floor(
    (
      milliseconds %
      60000
    ) / 1000,
  );

  return `${minutes} min ${seconds} s`;
}


function getInvoiceNumber(
  run,
  invoices,
) {
  if (run?.result?.invoice_number) {
    return run.result.invoice_number;
  }

  const invoice = invoices.find(
    (item) =>
      item.id === run?.invoice_id,
  );

  return (
    invoice?.invoice_number ||
    (
      run?.invoice_id
        ? `Factura #${run.invoice_id}`
        : "Factura no disponible"
    )
  );
}


function getProviderName(
  invoice,
) {
  return (
    invoice?.provider_name ||
    invoice?.detected_provider_name ||
    "Proveedor no identificado"
  );
}


export default function AutomationsPage() {
  const [runs, setRuns] =
    useState([]);

  const [invoices, setInvoices] =
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

  const [startOpen, setStartOpen] =
    useState(false);

  const [
    selectedInvoiceId,
    setSelectedInvoiceId,
  ] = useState("");

  const [starting, setStarting] =
    useState(false);

  const [startError, setStartError] =
    useState("");

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [selectedRun, setSelectedRun] =
    useState(null);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const [actionError, setActionError] =
    useState("");

  const [
    downloadingEvidence,
    setDownloadingEvidence,
  ] = useState(false);


  const loadInvoices =
    useCallback(async () => {
      try {
        const response =
          await apiClient.get(
            "/invoices",
            {
              params: {
                page: 1,
                page_size: 100,
                status: "PROCESSED",
              },
            },
          );

        setInvoices(
          normalizeCollection(
            response.data,
          ),
        );
      } catch (requestError) {
        setPageError(
          getApiErrorMessage(
            requestError,
            "No fue posible cargar las facturas procesadas.",
          ),
        );
      }
    }, []);


  const loadRuns = useCallback(
    async ({
      silent = false,
    } = {}) => {
      if (!silent) {
        setLoading(true);
      }

      try {
        const response =
          await apiClient.get(
            "/automations/rpa",
            {
              params: {
                page: 1,
                page_size: 100,
              },
            },
          );

        setRuns(
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
              "No fue posible cargar las automatizaciones.",
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
    loadInvoices();
    loadRuns();
  }, [
    loadInvoices,
    loadRuns,
  ]);


  const hasActiveRuns = useMemo(
    () =>
      runs.some((run) =>
        activeStatuses.includes(
          run.status,
        ),
      ),
    [runs],
  );


  useEffect(() => {
    if (!hasActiveRuns) {
      return undefined;
    }

    const intervalId =
      window.setInterval(
        () => {
          loadRuns({
            silent: true,
          });
        },
        3000,
      );

    return () => {
      window.clearInterval(
        intervalId,
      );
    };
  }, [
    hasActiveRuns,
    loadRuns,
  ]);


  const filteredRuns = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return runs.filter((run) => {
      const matchesStatus =
        !statusFilter ||
        run.status === statusFilter;

      const values = [
        run.id,
        run.invoice_id,
        run.automation_type,
        run.status,
        run.target_url,
        run.result?.invoice_number,
        run.result?.submission_id,
        run.result?.message,
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
    runs,
    search,
    statusFilter,
  ]);


  const metrics = useMemo(() => {
    const successful = runs.filter(
      (run) =>
        run.status === "SUCCESS",
    ).length;

    const active = runs.filter(
      (run) =>
        activeStatuses.includes(
          run.status,
        ),
    ).length;

    const failed = runs.filter(
      (run) =>
        [
          "ERROR",
          "FAILED",
        ].includes(run.status),
    ).length;

    const withEvidence = runs.filter(
      (run) =>
        Boolean(run.evidence_path),
    ).length;

    return {
      total: runs.length,
      successful,
      active,
      failed,
      withEvidence,
    };
  }, [runs]);


  const selectedInvoice = useMemo(
    () =>
      invoices.find(
        (invoice) =>
          invoice.id ===
          Number(selectedInvoiceId),
      ) || null,
    [
      invoices,
      selectedInvoiceId,
    ],
  );


  function openStartModal() {
    setSelectedInvoiceId("");
    setStartError("");
    setMessage("");
    setStartOpen(true);
  }


  function closeStartModal() {
    if (starting) {
      return;
    }

    setStartOpen(false);
    setStartError("");
  }


  async function startAutomation(event) {
    event.preventDefault();

    if (!selectedInvoiceId) {
      setStartError(
        "Seleccione una factura procesada.",
      );

      return;
    }

    setStarting(true);
    setStartError("");
    setMessage("");

    try {
      const response =
        await apiClient.post(
          `/automations/rpa/invoices/${selectedInvoiceId}`,
        );

      setStartOpen(false);

      setMessage(
        response.data?.message ||
        "La automatización fue enviada a ejecución.",
      );

      await loadRuns();

      window.setTimeout(
        () => {
          loadRuns({
            silent: true,
          });
        },
        3000,
      );
    } catch (requestError) {
      setStartError(
        getApiErrorMessage(
          requestError,
          "No fue posible iniciar la automatización.",
        ),
      );
    } finally {
      setStarting(false);
    }
  }


  async function openRunDetail(run) {
    setSelectedRun(run);
    setDetailOpen(true);
    setDetailLoading(true);
    setActionError("");

    try {
      const response =
        await apiClient.get(
          `/automations/rpa/${run.id}`,
        );

      setSelectedRun(
        response.data,
      );
    } catch (requestError) {
      setActionError(
        getApiErrorMessage(
          requestError,
          "No fue posible consultar la automatización.",
        ),
      );
    } finally {
      setDetailLoading(false);
    }
  }


  function closeDetailModal() {
    if (downloadingEvidence) {
      return;
    }

    setDetailOpen(false);
    setSelectedRun(null);
    setActionError("");
  }


  async function downloadEvidence(run) {
    setDownloadingEvidence(true);
    setActionError("");

    try {
      const response =
        await apiClient.get(
          `/automations/rpa/${run.id}/evidence`,
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
        `smartinvoice_rpa_${run.id}.png`;

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
          "No fue posible descargar la evidencia.",
        ),
      );
    } finally {
      setDownloadingEvidence(false);
    }
  }


  return (
    <div className="automations-page">
      <header className="page-header">
        <div>
          <span className="section-kicker">
            Automatización empresarial
          </span>

          <h1>Automatizaciones RPA</h1>

          <p>
            Registre facturas en sistemas
            externos y consulte el resultado
            y la evidencia de cada ejecución.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={openStartModal}
        >
          <Play size={18} />
          Nueva ejecución
        </button>
      </header>

      <section className="automation-metric-grid">
        <article className="automation-metric automation-metric-blue">
          <Bot size={21} />

          <div>
            <span>Total de ejecuciones</span>
            <strong>{metrics.total}</strong>
          </div>
        </article>

        <article className="automation-metric automation-metric-green">
          <CheckCircle2 size={21} />

          <div>
            <span>Completadas</span>
            <strong>
              {metrics.successful}
            </strong>
          </div>
        </article>

        <article className="automation-metric automation-metric-orange">
          <Activity
            size={21}
            className={
              metrics.active > 0
                ? "spin"
                : ""
            }
          />

          <div>
            <span>En ejecución</span>
            <strong>{metrics.active}</strong>
          </div>
        </article>

        <article className="automation-metric automation-metric-violet">
          <Image size={21} />

          <div>
            <span>Con evidencia</span>
            <strong>
              {metrics.withEvidence}
            </strong>
          </div>
        </article>

        <article className="automation-metric automation-metric-red">
          <TriangleAlert size={21} />

          <div>
            <span>Fallidas</span>
            <strong>{metrics.failed}</strong>
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

      <section className="content-card automations-table-card">
        <div className="table-toolbar">
          <div className="search-input">
            <Search size={18} />

            <input
              type="search"
              value={search}
              placeholder="Buscar ejecución, factura o registro externo"
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

              <option value="RUNNING">
                En ejecución
              </option>

              <option value="SUCCESS">
                Exitosas
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
                loadRuns()
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
              Cargando automatizaciones...
            </p>
          </div>
        ) : (
          <>
            <div className="table-result-summary">
              <span>
                {filteredRuns.length}
                {" "}
                resultado
                {filteredRuns.length === 1
                  ? ""
                  : "s"}
              </span>

              {hasActiveRuns && (
                <span className="live-processing-indicator">
                  <span />
                  Actualización automática activa
                </span>
              )}
            </div>

            {filteredRuns.length === 0 ? (
              <div className="table-state">
                <Bot size={39} />

                <h3>
                  No existen ejecuciones RPA
                </h3>

                <p>
                  Inicie una automatización o
                  modifique los filtros.
                </p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table automation-table">
                  <thead>
                    <tr>
                      <th>Ejecución</th>
                      <th>Factura</th>
                      <th>Registro externo</th>
                      <th>Duración</th>
                      <th>Fecha</th>
                      <th>Estado</th>
                      <th className="table-actions-column">
                        Acciones
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredRuns.map(
                      (run) => (
                        <tr key={run.id}>
                          <td>
                            <div className="table-primary-cell">
                              <div className="table-avatar automation-avatar">
                                <Bot size={18} />
                              </div>

                              <div>
                                <strong>
                                  Ejecución #{run.id}
                                </strong>

                                <span>
                                  {run.automation_type ===
                                  "REGISTER_INVOICE"
                                    ? "Registro de factura"
                                    : run.automation_type}
                                </span>
                              </div>
                            </div>
                          </td>

                          <td>
                            <div className="stacked-value">
                              <span>
                                {getInvoiceNumber(
                                  run,
                                  invoices,
                                )}
                              </span>

                              <small>
                                ID:
                                {" "}
                                {run.invoice_id ||
                                  "—"}
                              </small>
                            </div>
                          </td>

                          <td>
                            <div className="stacked-value">
                              <span>
                                {run.result
                                  ?.submission_id
                                  ? `Registro #${run.result.submission_id}`
                                  : "Pendiente"}
                              </span>

                              <small>
                                {run.result?.message ||
                                  "Sin respuesta externa"}
                              </small>
                            </div>
                          </td>

                          <td>
                            {formatDuration(
                              run.started_at,
                              run.finished_at,
                            )}
                          </td>

                          <td>
                            {formatDateTime(
                              run.created_at,
                            )}
                          </td>

                          <td>
                            <StatusBadge
                              status={
                                run.status
                              }
                            />
                          </td>

                          <td>
                            <div className="row-actions">
                              <button
                                className="table-icon-button"
                                type="button"
                                title="Consultar ejecución"
                                onClick={() =>
                                  openRunDetail(run)
                                }
                              >
                                <Eye size={17} />
                              </button>

                              <button
                                className="table-icon-button automation-evidence-button"
                                type="button"
                                title="Descargar evidencia"
                                disabled={
                                  !run.evidence_path ||
                                  downloadingEvidence
                                }
                                onClick={() =>
                                  downloadEvidence(run)
                                }
                              >
                                <Download
                                  size={17}
                                />
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
        open={startOpen}
        title="Nueva ejecución RPA"
        subtitle="Seleccione una factura procesada para registrarla en el sistema externo."
        onClose={closeStartModal}
      >
        <form
          className="modal-form"
          onSubmit={startAutomation}
        >
          <section className="automation-explanation">
            <div>
              <Bot size={24} />
            </div>

            <div>
              <strong>
                Registro automatizado
              </strong>

              <p>
                El robot abrirá el formulario
                externo, ingresará los datos de
                la factura, enviará el registro
                y guardará una captura como
                evidencia.
              </p>
            </div>
          </section>

          <label className="form-field">
            <span>Factura procesada</span>

            <select
              className="select-control"
              required
              value={selectedInvoiceId}
              onChange={(event) =>
                setSelectedInvoiceId(
                  event.target.value,
                )
              }
            >
              <option value="">
                Seleccione una factura
              </option>

              {invoices.map(
                (invoice) => (
                  <option
                    key={invoice.id}
                    value={invoice.id}
                  >
                    {invoice.invoice_number ||
                      `Factura #${invoice.id}`}
                    {" · "}
                    {getProviderName(invoice)}
                  </option>
                ),
              )}
            </select>
          </label>

          {selectedInvoice && (
            <section className="automation-invoice-preview">
              <div className="automation-preview-icon">
                <FileText size={21} />
              </div>

              <div>
                <span>
                  Factura seleccionada
                </span>

                <strong>
                  {selectedInvoice.invoice_number ||
                    `Factura #${selectedInvoice.id}`}
                </strong>

                <small>
                  {getProviderName(
                    selectedInvoice,
                  )}
                </small>
              </div>

              <StatusBadge
                status={
                  selectedInvoice.status
                }
              />
            </section>
          )}

          {invoices.length === 0 && (
            <div className="form-alert form-alert-error">
              No existen facturas procesadas
              disponibles para automatización.
            </div>
          )}

          {startError && (
            <div className="form-alert form-alert-error">
              {startError}
            </div>
          )}

          <footer className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              disabled={starting}
              onClick={closeStartModal}
            >
              Cancelar
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={
                starting ||
                !selectedInvoiceId
              }
            >
              {starting ? (
                <LoaderCircle
                  className="spin"
                  size={17}
                />
              ) : (
                <Play size={17} />
              )}

              Ejecutar robot
            </button>
          </footer>
        </form>
      </Modal>

      <Modal
        open={detailOpen}
        title={
          selectedRun
            ? `Ejecución RPA #${selectedRun.id}`
            : "Detalle de automatización"
        }
        subtitle={
          selectedRun
            ? getInvoiceNumber(
                selectedRun,
                invoices,
              )
            : "Resultado de la ejecución"
        }
        size="large"
        onClose={closeDetailModal}
      >
        {detailLoading ? (
          <div className="table-state automation-detail-loader">
            <LoaderCircle
              className="spin"
              size={30}
            />

            <p>
              Consultando ejecución...
            </p>
          </div>
        ) : selectedRun ? (
          <div className="automation-detail">
            {actionError && (
              <div className="form-alert form-alert-error">
                {actionError}
              </div>
            )}

            <section className="automation-detail-hero">
              <div className="automation-detail-title">
                <div>
                  <Bot size={25} />
                </div>

                <div>
                  <span>
                    Automatización
                  </span>

                  <strong>
                    Registro de factura
                  </strong>

                  <small>
                    {getInvoiceNumber(
                      selectedRun,
                      invoices,
                    )}
                  </small>
                </div>
              </div>

              <StatusBadge
                status={
                  selectedRun.status
                }
              />
            </section>

            <section className="automation-detail-grid">
              <article>
                <FileText size={18} />

                <div>
                  <span>Factura</span>

                  <strong>
                    {getInvoiceNumber(
                      selectedRun,
                      invoices,
                    )}
                  </strong>
                </div>
              </article>

              <article>
                <Server size={18} />

                <div>
                  <span>
                    Registro externo
                  </span>

                  <strong>
                    {selectedRun.result
                      ?.submission_id
                      ? `#${selectedRun.result.submission_id}`
                      : "No disponible"}
                  </strong>
                </div>
              </article>

              <article>
                <Clock3 size={18} />

                <div>
                  <span>Duración</span>

                  <strong>
                    {formatDuration(
                      selectedRun.started_at,
                      selectedRun.finished_at,
                    )}
                  </strong>
                </div>
              </article>

              <article>
                <CheckCircle2 size={18} />

                <div>
                  <span>Finalizada</span>

                  <strong>
                    {formatDateTime(
                      selectedRun.finished_at,
                    )}
                  </strong>
                </div>
              </article>
            </section>

            <section className="automation-result-panel">
              <header>
                <div>
                  <Activity size={18} />

                  <strong>
                    Respuesta del sistema externo
                  </strong>
                </div>
              </header>

              {Object.keys(
                selectedRun.result || {},
              ).length === 0 ? (
                <p>
                  La ejecución todavía no posee
                  un resultado disponible.
                </p>
              ) : (
                <dl>
                  <div>
                    <dt>Mensaje</dt>
                    <dd>
                      {selectedRun.result
                        ?.message || "—"}
                    </dd>
                  </div>

                  <div>
                    <dt>
                      Número de factura
                    </dt>
                    <dd>
                      {selectedRun.result
                        ?.invoice_number || "—"}
                    </dd>
                  </div>

                  <div>
                    <dt>
                      Identificador externo
                    </dt>
                    <dd>
                      {selectedRun.result
                        ?.submission_id || "—"}
                    </dd>
                  </div>

                  <div>
                    <dt>Destino utilizado</dt>
                    <dd>
                      {selectedRun.result
                        ?.target_url ||
                        selectedRun.target_url ||
                        "—"}
                    </dd>
                  </div>
                </dl>
              )}
            </section>

            {selectedRun.error_message && (
              <div className="form-alert form-alert-error">
                {selectedRun.error_message}
              </div>
            )}

            <footer className="automation-detail-actions">
              <button
                className="primary-button"
                type="button"
                disabled={
                  !selectedRun.evidence_path ||
                  downloadingEvidence
                }
                onClick={() =>
                  downloadEvidence(
                    selectedRun,
                  )
                }
              >
                {downloadingEvidence ? (
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />
                ) : (
                  <Download size={17} />
                )}

                Descargar evidencia
              </button>
            </footer>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
