import {
  AlertCircle,
  Bot,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  Download,
  Eye,
  FileImage,
  FileSearch,
  FileText,
  Files,
  LoaderCircle,
  RefreshCw,
  RotateCcw,
  ScanLine,
  Search,
  Upload,
  X,
  XCircle,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import apiClient, {
  getApiErrorMessage,
} from "../api/client";

import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";


const statusOptions = [
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


function normalizeCollection(
  value,
  preferredKey = "items",
) {
  if (Array.isArray(value)) {
    return value;
  }

  if (
    value &&
    Array.isArray(value[preferredKey])
  ) {
    return value[preferredKey];
  }

  const alternatives = [
    "items",
    "results",
    "logs",
    "data",
  ];

  for (const key of alternatives) {
    if (Array.isArray(value?.[key])) {
      return value[key];
    }
  }

  return [];
}


function formatCurrency(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  return new Intl.NumberFormat(
    "es-GT",
    {
      style: "currency",
      currency: "GTQ",
    },
  ).format(Number(value));
}


function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = String(value).includes("T")
    ? new Date(value)
    : new Date(`${value}T12:00:00`);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
    },
  ).format(date);
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


function formatFileSize(bytes) {
  if (!Number.isFinite(bytes)) {
    return "";
  }

  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${Math.ceil(bytes / 1024)} KB`;
  }

  return (
    `${(
      bytes /
      1024 /
      1024
    ).toFixed(2)} MB`
  );
}


function getConfidence(invoice) {
  const value =
    invoice?.ocr_confidence ??
    invoice?.confidence ??
    0;

  const numericValue = Number(value);

  return Number.isFinite(numericValue)
    ? numericValue
    : 0;
}


function getProviderName(invoice) {
  return (
    invoice?.provider_name ||
    invoice?.detected_provider_name ||
    "Proveedor no identificado"
  );
}


function getInvoiceNumber(invoice) {
  return (
    invoice?.invoice_number ||
    `Documento #${invoice?.id || ""}`
  );
}


function createReviewForm(invoice) {
  return {
    invoice_number:
      invoice?.invoice_number || "",

    invoice_date:
      invoice?.invoice_date || "",

    provider_id:
      invoice?.provider_id
        ? String(invoice.provider_id)
        : "",

    category_id:
      invoice?.category_id
        ? String(invoice.category_id)
        : "",

    nit:
      invoice?.detected_nit ||
      invoice?.nit ||
      "",

    subtotal:
      invoice?.subtotal ?? "",

    tax:
      invoice?.tax ?? "",

    total:
      invoice?.total ?? "",

    currency:
      invoice?.currency || "GTQ",
  };
}


function describeValidationIssue(issue) {
  if (typeof issue === "string") {
    return issue;
  }

  return (
    issue?.message ||
    issue?.detail ||
    issue?.error ||
    JSON.stringify(issue)
  );
}


export default function InvoicesPage() {
  const fileInputRef = useRef(null);

  const [invoices, setInvoices] =
    useState([]);

  const [providers, setProviders] =
    useState([]);

  const [categories, setCategories] =
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

  const [uploadOpen, setUploadOpen] =
    useState(false);

  const [selectedFiles, setSelectedFiles] =
    useState([]);

  const [
    selectedProviderId,
    setSelectedProviderId,
  ] = useState("");

  const [
    selectedCategoryId,
    setSelectedCategoryId,
  ] = useState("");

  const [uploading, setUploading] =
    useState(false);

  const [uploadError, setUploadError] =
    useState("");

  const [dragActive, setDragActive] =
    useState(false);

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [detailLoading, setDetailLoading] =
    useState(false);

  const [
    selectedInvoice,
    setSelectedInvoice,
  ] = useState(null);

  const [ocrData, setOcrData] =
    useState(null);

  const [logs, setLogs] =
    useState([]);

  const [activeTab, setActiveTab] =
    useState("data");

  const [detailError, setDetailError] =
    useState("");

  const [detailMessage, setDetailMessage] =
    useState("");

  const [actionLoading, setActionLoading] =
    useState(false);

  const [reviewForm, setReviewForm] =
    useState(null);


  const loadCatalogs =
    useCallback(async () => {
      try {
        const [
          providersResponse,
          categoriesResponse,
        ] = await Promise.all([
          apiClient.get("/providers", {
            params: {
              page: 1,
              page_size: 100,
            },
          }),

          apiClient.get("/categories"),
        ]);

        setProviders(
          normalizeCollection(
            providersResponse.data,
          ).filter(
            (provider) =>
              provider.is_active !== false,
          ),
        );

        setCategories(
          normalizeCollection(
            categoriesResponse.data,
          ),
        );
      } catch (requestError) {
        setPageError(
          getApiErrorMessage(
            requestError,
            "No fue posible cargar los catálogos.",
          ),
        );
      }
    }, []);


  const loadInvoices = useCallback(
    async ({
      silent = false,
    } = {}) => {
      if (!silent) {
        setLoading(true);
      }

      try {
        const params = {
          page: 1,
          page_size: 100,
        };

        if (statusFilter) {
          params.status = statusFilter;
        }

        const response =
          await apiClient.get(
            "/invoices",
            { params },
          );

        setInvoices(
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
              "No fue posible cargar las facturas.",
            ),
          );
        }
      } finally {
        if (!silent) {
          setLoading(false);
        }
      }
    },
    [statusFilter],
  );


  useEffect(() => {
    loadCatalogs();
  }, [loadCatalogs]);


  useEffect(() => {
    loadInvoices();
  }, [loadInvoices]);


  const hasActiveProcessing = useMemo(
    () =>
      invoices.some((invoice) =>
        [
          "PENDING",
          "PROCESSING",
        ].includes(invoice.status),
      ),
    [invoices],
  );


  useEffect(() => {
    if (!hasActiveProcessing) {
      return undefined;
    }

    const intervalId = window.setInterval(
      () => {
        loadInvoices({
          silent: true,
        });
      },
      5000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [
    hasActiveProcessing,
    loadInvoices,
  ]);


  const filteredInvoices = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    if (!normalizedSearch) {
      return invoices;
    }

    return invoices.filter((invoice) => {
      const values = [
        invoice.invoice_number,
        invoice.original_file_name,
        invoice.provider_name,
        invoice.detected_provider_name,
        invoice.detected_nit,
        invoice.nit,
        invoice.currency,
      ]
        .filter(Boolean)
        .map((value) =>
          String(value).toLowerCase(),
        );

      return values.some((value) =>
        value.includes(normalizedSearch),
      );
    });
  }, [invoices, search]);


  const invoiceMetrics = useMemo(() => {
    const processed = invoices.filter(
      (invoice) =>
        invoice.status === "PROCESSED",
    ).length;

    const processing = invoices.filter(
      (invoice) =>
        [
          "PENDING",
          "PROCESSING",
        ].includes(invoice.status),
    ).length;

    const exceptions = invoices.filter(
      (invoice) =>
        [
          "ERROR",
          "REJECTED",
          "DUPLICATE",
        ].includes(invoice.status),
    ).length;

    const totalAmount = invoices
      .filter(
        (invoice) =>
          invoice.status === "PROCESSED",
      )
      .reduce(
        (sum, invoice) =>
          sum +
          Number(invoice.total || 0),
        0,
      );

    return {
      total: invoices.length,
      processed,
      processing,
      exceptions,
      totalAmount,
    };
  }, [invoices]);


  function resetUploadForm() {
    setSelectedFiles([]);
    setSelectedProviderId("");
    setSelectedCategoryId("");
    setUploadError("");
    setDragActive(false);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }


  function openUploadModal() {
    resetUploadForm();
    setMessage("");
    setPageError("");
    setUploadOpen(true);
  }


  function closeUploadModal() {
    if (uploading) {
      return;
    }

    setUploadOpen(false);
    resetUploadForm();
  }


  function validateFiles(files) {
    const acceptedExtensions = [
      ".pdf",
      ".jpg",
      ".jpeg",
      ".png",
    ];

    const validFiles = files.filter(
      (file) => {
        const lowerName =
          file.name.toLowerCase();

        return acceptedExtensions.some(
          (extension) =>
            lowerName.endsWith(extension),
        );
      },
    );

    if (validFiles.length !== files.length) {
      setUploadError(
        "Solo se aceptan archivos PDF, JPG, JPEG y PNG.",
      );

      return [];
    }

    if (validFiles.length > 20) {
      setUploadError(
        "Puede seleccionar un máximo de veinte archivos.",
      );

      return validFiles.slice(0, 20);
    }

    setUploadError("");

    return validFiles;
  }


  function addFiles(files) {
    const incomingFiles =
      validateFiles(
        Array.from(files || []),
      );

    if (incomingFiles.length === 0) {
      return;
    }

    setSelectedFiles((current) => {
      const combined = [
        ...current,
        ...incomingFiles,
      ];

      const uniqueFiles = combined.filter(
        (file, index, collection) =>
          collection.findIndex(
            (candidate) =>
              candidate.name === file.name &&
              candidate.size === file.size &&
              candidate.lastModified ===
                file.lastModified,
          ) === index,
      );

      if (uniqueFiles.length > 20) {
        setUploadError(
          "Puede seleccionar un máximo de veinte archivos.",
        );
      }

      return uniqueFiles.slice(0, 20);
    });
  }


  function removeFile(index) {
    setSelectedFiles((current) =>
      current.filter(
        (_, currentIndex) =>
          currentIndex !== index,
      ),
    );
  }


  async function uploadInvoices(event) {
    event.preventDefault();

    if (selectedFiles.length === 0) {
      setUploadError(
        "Seleccione por lo menos un documento.",
      );

      return;
    }

    setUploading(true);
    setUploadError("");
    setMessage("");

    try {
      const formData = new FormData();

      if (selectedProviderId) {
        formData.append(
          "provider_id",
          selectedProviderId,
        );
      }

      if (selectedCategoryId) {
        formData.append(
          "category_id",
          selectedCategoryId,
        );
      }

      let response;

      if (selectedFiles.length === 1) {
        formData.append(
          "file",
          selectedFiles[0],
        );

        response = await apiClient.post(
          "/invoices/upload",
          formData,
        );

        const duplicate =
          response.data?.is_duplicate ||
          response.data?.invoice?.status ===
            "DUPLICATE";

        setMessage(
          duplicate
            ? "El documento fue registrado como duplicado."
            : "La factura fue cargada y enviada al procesamiento.",
        );
      } else {
        selectedFiles.forEach((file) => {
          formData.append(
            "files",
            file,
          );
        });

        response = await apiClient.post(
          "/invoices/batch",
          formData,
        );

        const successful =
          response.data?.successful ??
          response.data?.success_count ??
          selectedFiles.length;

        const duplicates =
          response.data?.duplicates ??
          response.data?.duplicate_count ??
          0;

        const failed =
          response.data?.failed ??
          response.data?.failed_count ??
          0;

        setMessage(
          `Carga completada: ${successful} aceptadas, ` +
          `${duplicates} duplicadas y ${failed} rechazadas.`,
        );
      }

      setUploadOpen(false);
      resetUploadForm();

      await loadInvoices();

      window.setTimeout(
        () => {
          loadInvoices({
            silent: true,
          });
        },
        4000,
      );
    } catch (requestError) {
      setUploadError(
        getApiErrorMessage(
          requestError,
          "No fue posible cargar los documentos.",
        ),
      );
    } finally {
      setUploading(false);
    }
  }


  async function loadInvoiceDetail(
    invoiceId,
    fallbackInvoice = null,
  ) {
    setDetailLoading(true);
    setDetailError("");
    setDetailMessage("");
    setOcrData(null);
    setLogs([]);

    const [
      detailResult,
      ocrResult,
      logsResult,
    ] = await Promise.allSettled([
      apiClient.get(
        `/invoices/${invoiceId}`,
      ),

      apiClient.get(
        `/invoices/${invoiceId}/ocr`,
      ),

      apiClient.get(
        `/invoices/${invoiceId}/logs`,
      ),
    ]);

    const invoice =
      detailResult.status === "fulfilled"
        ? detailResult.value.data
        : fallbackInvoice;

    if (invoice) {
      setSelectedInvoice(invoice);
      setReviewForm(
        createReviewForm(invoice),
      );
    }

    if (ocrResult.status === "fulfilled") {
      setOcrData(
        ocrResult.value.data,
      );
    }

    if (logsResult.status === "fulfilled") {
      setLogs(
        normalizeCollection(
          logsResult.value.data,
          "items",
        ),
      );
    }

    if (
      detailResult.status === "rejected" &&
      !fallbackInvoice
    ) {
      setDetailError(
        getApiErrorMessage(
          detailResult.reason,
          "No fue posible cargar la factura.",
        ),
      );
    }

    setDetailLoading(false);
  }


  function openInvoiceDetail(invoice) {
    setSelectedInvoice(invoice);
    setReviewForm(
      createReviewForm(invoice),
    );
    setActiveTab("data");
    setDetailOpen(true);

    loadInvoiceDetail(
      invoice.id,
      invoice,
    );
  }


  function closeInvoiceDetail() {
    if (actionLoading) {
      return;
    }

    setDetailOpen(false);
    setDetailError("");
    setDetailMessage("");
  }


  async function openProtectedFile(
    endpoint,
    fileName,
  ) {
    setActionLoading(true);
    setDetailError("");

    try {
      const response =
        await apiClient.get(
          endpoint,
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
      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";
      anchor.download = fileName;

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      window.setTimeout(
        () => {
          URL.revokeObjectURL(objectUrl);
        },
        60000,
      );
    } catch (requestError) {
      setDetailError(
        getApiErrorMessage(
          requestError,
          "No fue posible abrir el archivo.",
        ),
      );
    } finally {
      setActionLoading(false);
    }
  }


  async function reprocessInvoice() {
    if (!selectedInvoice) {
      return;
    }

    const confirmed = window.confirm(
      "¿Desea ejecutar nuevamente el procesamiento OCR de esta factura?",
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(true);
    setDetailError("");
    setDetailMessage("");

    try {
      await apiClient.post(
        `/invoices/${selectedInvoice.id}/process`,
      );

      setDetailMessage(
        "La factura fue enviada nuevamente al procesamiento.",
      );

      await loadInvoices({
        silent: true,
      });

      window.setTimeout(
        () => {
          loadInvoiceDetail(
            selectedInvoice.id,
            selectedInvoice,
          );

          loadInvoices({
            silent: true,
          });
        },
        4000,
      );
    } catch (requestError) {
      setDetailError(
        getApiErrorMessage(
          requestError,
          "No fue posible reprocesar la factura.",
        ),
      );
    } finally {
      setActionLoading(false);
    }
  }


  async function executeRpa() {
    if (!selectedInvoice) {
      return;
    }

    const confirmed = window.confirm(
      "¿Desea registrar esta factura en el sistema externo mediante RPA?",
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(true);
    setDetailError("");
    setDetailMessage("");

    try {
      const response =
        await apiClient.post(
          `/automations/rpa/invoices/${selectedInvoice.id}`,
        );

      const runId =
        response.data?.automation?.id ||
        response.data?.id;

      setDetailMessage(
        runId
          ? `La automatización RPA #${runId} fue enviada a ejecución.`
          : "La automatización RPA fue enviada a ejecución.",
      );
    } catch (requestError) {
      setDetailError(
        getApiErrorMessage(
          requestError,
          "No fue posible iniciar la automatización RPA.",
        ),
      );
    } finally {
      setActionLoading(false);
    }
  }


  function updateReviewField(
    field,
    value,
  ) {
    setReviewForm((current) => ({
      ...current,
      [field]: value,
    }));

    if (field === "provider_id") {
      const provider = providers.find(
        (item) =>
          item.id === Number(value),
      );

      if (provider) {
        setReviewForm((current) => ({
          ...current,
          provider_id: value,
          nit: provider.nit || current.nit,
          category_id:
            current.category_id ||
            (
              provider.category_id
                ? String(
                    provider.category_id,
                  )
                : ""
            ),
        }));
      }
    }
  }


  async function saveReview(event) {
    event.preventDefault();

    if (
      !selectedInvoice ||
      !reviewForm
    ) {
      return;
    }

    setActionLoading(true);
    setDetailError("");
    setDetailMessage("");

    try {
      const payload = {
        invoice_number:
          reviewForm.invoice_number.trim(),

        invoice_date:
          reviewForm.invoice_date,

        provider_id:
          Number(reviewForm.provider_id),

        category_id:
          reviewForm.category_id
            ? Number(
                reviewForm.category_id,
              )
            : null,

        nit:
          reviewForm.nit.trim(),

        subtotal:
          Number(reviewForm.subtotal),

        tax:
          Number(reviewForm.tax),

        total:
          Number(reviewForm.total),

        currency:
          reviewForm.currency
            .trim()
            .toUpperCase(),
      };

      await apiClient.put(
        `/invoices/${selectedInvoice.id}/review`,
        payload,
      );

      setDetailMessage(
        "La revisión administrativa fue guardada correctamente.",
      );

      await loadInvoices({
        silent: true,
      });

      await loadInvoiceDetail(
        selectedInvoice.id,
        {
          ...selectedInvoice,
          ...payload,
        },
      );
    } catch (requestError) {
      setDetailError(
        getApiErrorMessage(
          requestError,
          "No fue posible guardar la revisión.",
        ),
      );
    } finally {
      setActionLoading(false);
    }
  }


  const extractedData =
    ocrData?.extracted_data ||
    ocrData?.data ||
    {};

  const rawOcrText =
    ocrData?.raw_text ||
    ocrData?.ocr_text ||
    ocrData?.text ||
    selectedInvoice?.ocr_text ||
    "";

  const validationErrors =
    normalizeCollection(
      ocrData?.validation_errors ||
      selectedInvoice?.validation_errors ||
      [],
    );

  const canRunRpa =
    selectedInvoice?.status ===
    "PROCESSED";

  const canReprocess =
    selectedInvoice &&
    ![
      "PROCESSING",
      "DUPLICATE",
    ].includes(
      selectedInvoice.status,
    );

  const canReview =
    selectedInvoice &&
    selectedInvoice.status !==
      "DUPLICATE";


  return (
    <div className="invoices-page">
      <header className="page-header">
        <div>
          <span className="section-kicker">
            Procesamiento documental
          </span>

          <h1>Facturas</h1>

          <p>
            Cargue documentos, revise los
            resultados OCR y controle cada
            etapa del procesamiento.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={openUploadModal}
        >
          <Upload size={18} />
          Cargar facturas
        </button>
      </header>

      <section className="invoice-metric-grid">
        <article className="invoice-metric invoice-metric-blue">
          <div className="invoice-metric-icon">
            <Files size={21} />
          </div>

          <div>
            <span>Total registrado</span>
            <strong>
              {invoiceMetrics.total}
            </strong>
          </div>
        </article>

        <article className="invoice-metric invoice-metric-green">
          <div className="invoice-metric-icon">
            <CheckCircle2 size={21} />
          </div>

          <div>
            <span>Procesadas</span>
            <strong>
              {invoiceMetrics.processed}
            </strong>
          </div>
        </article>

        <article className="invoice-metric invoice-metric-orange">
          <div className="invoice-metric-icon">
            <Clock3 size={21} />
          </div>

          <div>
            <span>En proceso</span>
            <strong>
              {invoiceMetrics.processing}
            </strong>
          </div>
        </article>

        <article className="invoice-metric invoice-metric-violet">
          <div className="invoice-metric-icon">
            <CircleDollarSign size={21} />
          </div>

          <div>
            <span>Monto procesado</span>
            <strong>
              {formatCurrency(
                invoiceMetrics.totalAmount,
              )}
            </strong>
          </div>
        </article>

        <article className="invoice-metric invoice-metric-red">
          <div className="invoice-metric-icon">
            <AlertCircle size={21} />
          </div>

          <div>
            <span>Excepciones</span>
            <strong>
              {invoiceMetrics.exceptions}
            </strong>
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

      <section className="content-card invoices-table-card">
        <div className="table-toolbar">
          <div className="search-input">
            <Search size={18} />

            <input
              type="search"
              value={search}
              placeholder="Buscar factura, proveedor, NIT o archivo"
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
              {statusOptions.map(
                (option) => (
                  <option
                    key={
                      option.value ||
                      "ALL"
                    }
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ),
              )}
            </select>

            <button
              className="secondary-button"
              type="button"
              disabled={loading}
              onClick={() =>
                loadInvoices()
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

            <p>Cargando facturas...</p>
          </div>
        ) : (
          <>
            <div className="table-result-summary">
              <span>
                {filteredInvoices.length}
                {" "}
                resultado
                {filteredInvoices.length === 1
                  ? ""
                  : "s"}
              </span>

              {hasActiveProcessing && (
                <span className="live-processing-indicator">
                  <span />
                  Actualización automática activa
                </span>
              )}
            </div>

            {filteredInvoices.length === 0 ? (
              <div className="table-state">
                <FileSearch size={37} />

                <h3>
                  No se encontraron facturas
                </h3>

                <p>
                  Modifique los filtros o
                  cargue nuevos documentos.
                </p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table invoice-table">
                  <thead>
                    <tr>
                      <th>Documento</th>
                      <th>Proveedor</th>
                      <th>Fecha</th>
                      <th>Total</th>
                      <th>Confianza OCR</th>
                      <th>Estado</th>
                      <th className="table-actions-column">
                        Acciones
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredInvoices.map(
                      (invoice) => {
                        const confidence =
                          getConfidence(
                            invoice,
                          );

                        return (
                          <tr key={invoice.id}>
                            <td>
                              <div className="table-primary-cell">
                                <div className="table-avatar invoice-table-avatar">
                                  <FileText
                                    size={18}
                                  />
                                </div>

                                <div>
                                  <strong>
                                    {getInvoiceNumber(
                                      invoice,
                                    )}
                                  </strong>

                                  <span>
                                    {invoice.original_file_name ||
                                      "Archivo sin nombre"}
                                  </span>
                                </div>
                              </div>
                            </td>

                            <td>
                              <div className="stacked-value">
                                <span>
                                  {getProviderName(
                                    invoice,
                                  )}
                                </span>

                                <small>
                                  {invoice.detected_nit ||
                                    invoice.nit ||
                                    "Sin NIT"}
                                </small>
                              </div>
                            </td>

                            <td>
                              {formatDate(
                                invoice.invoice_date,
                              )}
                            </td>

                            <td>
                              <strong className="invoice-total-value">
                                {formatCurrency(
                                  invoice.total,
                                )}
                              </strong>
                            </td>

                            <td>
                              {confidence > 0 ? (
                                <div className="confidence-cell">
                                  <div>
                                    <span
                                      style={{
                                        width:
                                          `${Math.min(
                                            confidence,
                                            100,
                                          )}%`,
                                      }}
                                    />
                                  </div>

                                  <strong>
                                    {confidence.toFixed(
                                      2,
                                    )}
                                    %
                                  </strong>
                                </div>
                              ) : (
                                <span className="muted-value">
                                  Pendiente
                                </span>
                              )}
                            </td>

                            <td>
                              <StatusBadge
                                status={
                                  invoice.status
                                }
                              />
                            </td>

                            <td>
                              <div className="row-actions">
                                <button
                                  className="table-icon-button"
                                  type="button"
                                  title="Consultar factura"
                                  onClick={() =>
                                    openInvoiceDetail(
                                      invoice,
                                    )
                                  }
                                >
                                  <Eye size={18} />
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
        open={uploadOpen}
        title="Cargar facturas"
        subtitle="Seleccione uno o varios documentos para enviarlos al procesamiento OCR."
        onClose={closeUploadModal}
      >
        <form
          className="modal-form"
          onSubmit={uploadInvoices}
        >
          <div
            className={[
              "invoice-upload-zone",
              dragActive
                ? "invoice-upload-zone-active"
                : "",
            ]
              .filter(Boolean)
              .join(" ")}
            role="button"
            tabIndex={0}
            onClick={() =>
              fileInputRef.current?.click()
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                fileInputRef.current?.click();
              }
            }}
            onDragEnter={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(event) => {
              event.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragActive(false);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setDragActive(false);
              addFiles(
                event.dataTransfer.files,
              );
            }}
          >
            <div className="invoice-upload-icon">
              <Upload size={27} />
            </div>

            <strong>
              Arrastre los documentos aquí
            </strong>

            <span>
              o presione para seleccionarlos
            </span>

            <small>
              PDF, JPG, JPEG o PNG · máximo 20 archivos
            </small>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(event) => {
                addFiles(
                  event.target.files,
                );

                event.target.value = "";
              }}
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="selected-invoice-files">
              <header>
                <strong>
                  Archivos seleccionados
                </strong>

                <span>
                  {selectedFiles.length}
                  /20
                </span>
              </header>

              <div>
                {selectedFiles.map(
                  (file, index) => (
                    <article
                      key={
                        `${file.name}-${file.size}-${file.lastModified}`
                      }
                    >
                      <div className="selected-file-icon">
                        {file.name
                          .toLowerCase()
                          .endsWith(".pdf") ? (
                          <FileText size={17} />
                        ) : (
                          <FileImage size={17} />
                        )}
                      </div>

                      <div className="selected-file-copy">
                        <strong>
                          {file.name}
                        </strong>

                        <span>
                          {formatFileSize(
                            file.size,
                          )}
                        </span>
                      </div>

                      <button
                        type="button"
                        aria-label="Eliminar archivo"
                        onClick={() =>
                          removeFile(index)
                        }
                      >
                        <X size={16} />
                      </button>
                    </article>
                  ),
                )}
              </div>
            </div>
          )}

          <div className="form-grid">
            <label className="form-field">
              <span>
                Proveedor preseleccionado
              </span>

              <select
                className="select-control"
                value={selectedProviderId}
                onChange={(event) => {
                  const value =
                    event.target.value;

                  setSelectedProviderId(
                    value,
                  );

                  const provider =
                    providers.find(
                      (item) =>
                        item.id ===
                        Number(value),
                    );

                  if (
                    provider?.category_id
                  ) {
                    setSelectedCategoryId(
                      String(
                        provider.category_id,
                      ),
                    );
                  }
                }}
              >
                <option value="">
                  Detectar automáticamente
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
              <span>Categoría</span>

              <select
                className="select-control"
                value={selectedCategoryId}
                onChange={(event) =>
                  setSelectedCategoryId(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Detectar automáticamente
                </option>

                {categories.map(
                  (category) => (
                    <option
                      key={category.id}
                      value={category.id}
                    >
                      {category.name}
                    </option>
                  ),
                )}
              </select>
            </label>
          </div>

          {uploadError && (
            <div className="form-alert form-alert-error">
              {uploadError}
            </div>
          )}

          <footer className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              disabled={uploading}
              onClick={closeUploadModal}
            >
              Cancelar
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={
                uploading ||
                selectedFiles.length === 0
              }
            >
              {uploading ? (
                <>
                  <LoaderCircle
                    className="spin"
                    size={17}
                  />

                  Cargando...
                </>
              ) : (
                <>
                  <Upload size={17} />

                  Procesar
                  {" "}
                  {selectedFiles.length > 0
                    ? selectedFiles.length
                    : ""}
                </>
              )}
            </button>
          </footer>
        </form>
      </Modal>

      <Modal
        open={detailOpen}
        title={
          selectedInvoice
            ? getInvoiceNumber(
                selectedInvoice,
              )
            : "Detalle de factura"
        }
        subtitle={
          selectedInvoice
            ?.original_file_name ||
          "Información procesada"
        }
        size="large"
        onClose={closeInvoiceDetail}
      >
        {detailLoading &&
        !selectedInvoice ? (
          <div className="table-state invoice-detail-loader">
            <LoaderCircle
              className="spin"
              size={31}
            />

            <p>
              Cargando información...
            </p>
          </div>
        ) : selectedInvoice ? (
          <div className="invoice-detail">
            {detailMessage && (
              <div className="form-alert form-alert-success">
                {detailMessage}
              </div>
            )}

            {detailError && (
              <div className="form-alert form-alert-error">
                {detailError}
              </div>
            )}

            <section className="invoice-detail-hero">
              <div className="invoice-detail-title">
                <div className="invoice-detail-document-icon">
                  <FileText size={25} />
                </div>

                <div>
                  <span>
                    Documento procesado
                  </span>

                  <strong>
                    {getInvoiceNumber(
                      selectedInvoice,
                    )}
                  </strong>

                  <small>
                    {getProviderName(
                      selectedInvoice,
                    )}
                  </small>
                </div>
              </div>

              <div className="invoice-detail-total">
                <span>Total</span>

                <strong>
                  {formatCurrency(
                    selectedInvoice.total,
                  )}
                </strong>

                <StatusBadge
                  status={
                    selectedInvoice.status
                  }
                />
              </div>
            </section>

            <section className="invoice-detail-stats">
              <article className="detail-stat-blue">
                <ScanLine size={18} />

                <div>
                  <span>Confianza OCR</span>
                  <strong>
                    {getConfidence(
                      selectedInvoice,
                    ).toFixed(2)}
                    %
                  </strong>
                </div>
              </article>

              <article className="detail-stat-green">
                <CircleDollarSign
                  size={18}
                />

                <div>
                  <span>Subtotal</span>
                  <strong>
                    {formatCurrency(
                      selectedInvoice.subtotal,
                    )}
                  </strong>
                </div>
              </article>

              <article className="detail-stat-orange">
                <FileText size={18} />

                <div>
                  <span>IVA</span>
                  <strong>
                    {formatCurrency(
                      selectedInvoice.tax,
                    )}
                  </strong>
                </div>
              </article>

              <article className="detail-stat-violet">
                <Clock3 size={18} />

                <div>
                  <span>Procesada</span>
                  <strong>
                    {formatDateTime(
                      selectedInvoice.processed_at,
                    )}
                  </strong>
                </div>
              </article>
            </section>

            <section className="invoice-detail-actions">
              <button
                className="secondary-button"
                type="button"
                disabled={actionLoading}
                onClick={() =>
                  openProtectedFile(
                    `/invoices/${selectedInvoice.id}/file`,
                    selectedInvoice.original_file_name ||
                      `factura_${selectedInvoice.id}`,
                  )
                }
              >
                <Download size={17} />
                Documento original
              </button>

              <button
                className="secondary-button"
                type="button"
                disabled={
                  actionLoading ||
                  !selectedInvoice.processed_file_path
                }
                onClick={() =>
                  openProtectedFile(
                    `/invoices/${selectedInvoice.id}/processed-file`,
                    `factura_${selectedInvoice.id}_procesada.png`,
                  )
                }
              >
                <FileImage size={17} />
                Imagen procesada
              </button>

              {canReprocess && (
                <button
                  className="secondary-button"
                  type="button"
                  disabled={actionLoading}
                  onClick={reprocessInvoice}
                >
                  <RotateCcw size={17} />
                  Reprocesar
                </button>
              )}

              {canRunRpa && (
                <button
                  className="primary-button"
                  type="button"
                  disabled={actionLoading}
                  onClick={executeRpa}
                >
                  <Bot size={17} />
                  Ejecutar RPA
                </button>
              )}
            </section>

            <nav className="invoice-detail-tabs">
              <button
                type="button"
                className={
                  activeTab === "data"
                    ? "invoice-tab-active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("data")
                }
              >
                Datos administrativos
              </button>

              <button
                type="button"
                className={
                  activeTab === "ocr"
                    ? "invoice-tab-active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("ocr")
                }
              >
                Resultado OCR
              </button>

              <button
                type="button"
                className={
                  activeTab === "logs"
                    ? "invoice-tab-active"
                    : ""
                }
                onClick={() =>
                  setActiveTab("logs")
                }
              >
                Bitácora
                <span>{logs.length}</span>
              </button>
            </nav>

            {activeTab === "data" &&
              reviewForm && (
                <section className="invoice-tab-panel">
                  <header className="invoice-panel-header">
                    <div>
                      <h3>
                        Revisión administrativa
                      </h3>

                      <p>
                        Verifique y corrija la
                        información detectada
                        antes de utilizarla.
                      </p>
                    </div>
                  </header>

                  <form
                    className="review-form"
                    onSubmit={saveReview}
                  >
                    <div className="form-grid">
                      <label className="form-field">
                        <span>
                          Número de factura
                        </span>

                        <input
                          className="text-control"
                          required
                          value={
                            reviewForm.invoice_number
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "invoice_number",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>Fecha</span>

                        <input
                          className="text-control"
                          type="date"
                          required
                          value={
                            reviewForm.invoice_date
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "invoice_date",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>Proveedor</span>

                        <select
                          className="select-control"
                          required
                          value={
                            reviewForm.provider_id
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "provider_id",
                              event.target.value,
                            )
                          }
                        >
                          <option value="">
                            Seleccione un proveedor
                          </option>

                          {providers.map(
                            (provider) => (
                              <option
                                key={
                                  provider.id
                                }
                                value={
                                  provider.id
                                }
                              >
                                {provider.name}
                              </option>
                            ),
                          )}
                        </select>
                      </label>

                      <label className="form-field">
                        <span>NIT</span>

                        <input
                          className="text-control"
                          required
                          value={reviewForm.nit}
                          onChange={(event) =>
                            updateReviewField(
                              "nit",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>Subtotal</span>

                        <input
                          className="text-control"
                          type="number"
                          min="0"
                          step="0.01"
                          required
                          value={
                            reviewForm.subtotal
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "subtotal",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>IVA</span>

                        <input
                          className="text-control"
                          type="number"
                          min="0"
                          step="0.01"
                          required
                          value={
                            reviewForm.tax
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "tax",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>Total</span>

                        <input
                          className="text-control"
                          type="number"
                          min="0"
                          step="0.01"
                          required
                          value={
                            reviewForm.total
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "total",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field">
                        <span>Moneda</span>

                        <input
                          className="text-control"
                          required
                          maxLength={3}
                          value={
                            reviewForm.currency
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "currency",
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label className="form-field form-field-wide">
                        <span>Categoría</span>

                        <select
                          className="select-control"
                          value={
                            reviewForm.category_id
                          }
                          onChange={(event) =>
                            updateReviewField(
                              "category_id",
                              event.target.value,
                            )
                          }
                        >
                          <option value="">
                            Sin categoría
                          </option>

                          {categories.map(
                            (category) => (
                              <option
                                key={
                                  category.id
                                }
                                value={
                                  category.id
                                }
                              >
                                {category.name}
                              </option>
                            ),
                          )}
                        </select>
                      </label>
                    </div>

                    {canReview && (
                      <div className="review-form-actions">
                        <button
                          className="primary-button"
                          type="submit"
                          disabled={actionLoading}
                        >
                          {actionLoading ? (
                            <LoaderCircle
                              className="spin"
                              size={17}
                            />
                          ) : (
                            <CheckCircle2
                              size={17}
                            />
                          )}

                          Guardar revisión
                        </button>
                      </div>
                    )}
                  </form>
                </section>
              )}

            {activeTab === "ocr" && (
              <section className="invoice-tab-panel">
                <header className="invoice-panel-header">
                  <div>
                    <h3>
                      Resultado del reconocimiento
                    </h3>

                    <p>
                      Información detectada por
                      Tesseract y procesada mediante
                      OpenCV.
                    </p>
                  </div>
                </header>

                <div className="ocr-data-grid">
                  <article>
                    <span>
                      Número detectado
                    </span>

                    <strong>
                      {extractedData.invoice_number ||
                        selectedInvoice.invoice_number ||
                        "No detectado"}
                    </strong>
                  </article>

                  <article>
                    <span>
                      Proveedor detectado
                    </span>

                    <strong>
                      {extractedData.provider_name ||
                        selectedInvoice.detected_provider_name ||
                        "No detectado"}
                    </strong>
                  </article>

                  <article>
                    <span>NIT detectado</span>

                    <strong>
                      {extractedData.nit ||
                        selectedInvoice.detected_nit ||
                        "No detectado"}
                    </strong>
                  </article>

                  <article>
                    <span>Total detectado</span>

                    <strong>
                      {formatCurrency(
                        extractedData.total ??
                          selectedInvoice.total,
                      )}
                    </strong>
                  </article>
                </div>

                {validationErrors.length > 0 && (
                  <div className="ocr-validation-panel">
                    <h4>
                      Observaciones de validación
                    </h4>

                    {validationErrors.map(
                      (issue, index) => (
                        <div key={index}>
                          <XCircle size={17} />

                          <span>
                            {describeValidationIssue(
                              issue,
                            )}
                          </span>
                        </div>
                      ),
                    )}
                  </div>
                )}

                <div className="ocr-text-panel">
                  <header>
                    <div>
                      <FileSearch size={19} />

                      <strong>
                        Texto reconocido
                      </strong>
                    </div>

                    <span>
                      {rawOcrText.length}
                      {" "}
                      caracteres
                    </span>
                  </header>

                  <pre>
                    {rawOcrText ||
                      "El texto OCR todavía no está disponible."}
                  </pre>
                </div>
              </section>
            )}

            {activeTab === "logs" && (
              <section className="invoice-tab-panel">
                <header className="invoice-panel-header">
                  <div>
                    <h3>
                      Bitácora de procesamiento
                    </h3>

                    <p>
                      Registro cronológico de cada
                      etapa ejecutada sobre el
                      documento.
                    </p>
                  </div>
                </header>

                {logs.length === 0 ? (
                  <div className="invoice-empty-panel">
                    <Clock3 size={29} />

                    <p>
                      No existen eventos registrados.
                    </p>
                  </div>
                ) : (
                  <div className="processing-timeline">
                    {logs.map(
                      (log, index) => (
                        <article
                          key={
                            log.id ||
                            `${log.stage}-${index}`
                          }
                        >
                          <div className="timeline-marker">
                            <span />
                          </div>

                          <div className="timeline-content">
                            <header>
                              <div>
                                <strong>
                                  {log.stage ||
                                    "PROCESO"}
                                </strong>

                                <span>
                                  {formatDateTime(
                                    log.started_at ||
                                      log.created_at,
                                  )}
                                </span>
                              </div>

                              <StatusBadge
                                status={
                                  log.status ||
                                  "SUCCESS"
                                }
                              />
                            </header>

                            <p>
                              {log.message ||
                                "Etapa procesada correctamente."}
                            </p>

                            {log.duration_ms !==
                              undefined &&
                              log.duration_ms !==
                                null && (
                              <small>
                                Duración:
                                {" "}
                                {log.duration_ms}
                                {" "}
                                ms
                              </small>
                            )}
                          </div>
                        </article>
                      ),
                    )}
                  </div>
                )}
              </section>
            )}
          </div>
        ) : (
          <div className="table-state">
            <AlertCircle size={31} />

            <p>
              No fue posible cargar la factura.
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
}
