import {
  AlertTriangle,
  CheckCircle2,
  CircleDollarSign,
  Files,
  LoaderCircle,
  RefreshCw,
  ScanLine,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import apiClient, {
  getApiErrorMessage,
} from "../api/client";


const statusLabels = {
  PENDING: "Pendientes",
  PROCESSING: "Procesando",
  PROCESSED: "Procesadas",
  REJECTED: "Rechazadas",
  ERROR: "Con error",
  DUPLICATE: "Duplicadas",
};

const statusColors = {
  PENDING: "#F2B705",
  PROCESSING: "#3B82F6",
  PROCESSED: "#22A06B",
  REJECTED: "#F97316",
  ERROR: "#DC4C64",
  DUPLICATE: "#8B5CF6",
};

const providerColors = [
  "#F2B705",
  "#3B82F6",
  "#22A06B",
  "#8B5CF6",
  "#F97316",
  "#0891B2",
];


function formatCurrency(value) {
  return new Intl.NumberFormat(
    "es-GT",
    {
      style: "currency",
      currency: "GTQ",
    },
  ).format(Number(value || 0));
}


function formatNumber(value) {
  return new Intl.NumberFormat(
    "es-GT",
  ).format(Number(value || 0));
}


export default function DashboardPage() {
  const [dashboard, setDashboard] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  const loadDashboard =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const response = await apiClient.get(
          "/dashboard/summary",
        );

        setDashboard(response.data);
      } catch (requestError) {
        setError(
          getApiErrorMessage(
            requestError,
            "No fue posible cargar el dashboard.",
          ),
        );
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);


  const statusData = useMemo(
    () =>
      (dashboard?.by_status || []).map(
        (item) => ({
          name:
            statusLabels[item.status] ||
            item.status,
          value: item.invoice_count,
          status: item.status,
        }),
      ),
    [dashboard],
  );


  const providerData = useMemo(
    () =>
      (dashboard?.by_provider || [])
        .filter(
          (provider) =>
            provider.invoice_count > 0,
        )
        .slice(0, 6)
        .map((provider) => ({
          name: provider.provider_name,
          total: Number(
            provider.total_amount,
          ),
        })),
    [dashboard],
  );


  const currentDate =
    new Intl.DateTimeFormat(
      "es-GT",
      {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      },
    ).format(new Date());


  if (loading) {
    return (
      <section className="page-state">
        <LoaderCircle
          className="spin"
          size={31}
        />

        <p>Cargando indicadores...</p>
      </section>
    );
  }


  if (error) {
    return (
      <section className="page-state">
        <AlertTriangle size={34} />

        <h2>
          No se pudo cargar el dashboard
        </h2>

        <p>{error}</p>

        <button
          className="secondary-button"
          type="button"
          onClick={loadDashboard}
        >
          <RefreshCw size={17} />
          Reintentar
        </button>
      </section>
    );
  }


  const summary = dashboard.summary;


  const metrics = [
    {
      label: "Facturas registradas",
      value: formatNumber(
        summary.total_invoices,
      ),
      detail: "Documentos en el sistema",
      icon: Files,
      variant: "blue",
    },
    {
      label: "Procesadas",
      value: formatNumber(
        summary.processed_invoices,
      ),
      detail: "Validación completada",
      icon: CheckCircle2,
      variant: "green",
    },
    {
      label: "Monto acumulado",
      value: formatCurrency(
        summary.processed_total,
      ),
      detail: "Facturación procesada",
      icon: CircleDollarSign,
      variant: "violet",
    },
    {
      label: "Confianza OCR",
      value:
        `${Number(
          summary.average_ocr_confidence,
        ).toFixed(2)} %`,
      detail: "Promedio de reconocimiento",
      icon: ScanLine,
      variant: "orange",
    },
  ];


  return (
    <div className="dashboard-page">
      <header className="page-header dashboard-header">
        <div>
          <span className="section-kicker">
            Resumen administrativo
          </span>

          <h1>
            Control de facturación
          </h1>

          <p>
            Consulte el estado general del
            procesamiento documental.
          </p>
        </div>

        <div className="dashboard-header-actions">
          <span className="dashboard-date">
            {currentDate}
          </span>

          <button
            className="secondary-button"
            type="button"
            onClick={loadDashboard}
          >
            <RefreshCw size={17} />
            Actualizar
          </button>
        </div>
      </header>

      <section className="metric-grid">
        {metrics.map(
          ({
            label,
            value,
            detail,
            icon: Icon,
            variant,
          }) => (
            <article
              className={
                `metric-card metric-card-${variant}`
              }
              key={label}
            >
              <div className="metric-card-top">
                <span>{label}</span>

                <div
                  className={
                    `metric-icon metric-icon-${variant}`
                  }
                >
                  <Icon size={20} />
                </div>
              </div>

              <strong>{value}</strong>

              <small>{detail}</small>
            </article>
          ),
        )}
      </section>

      <section className="dashboard-grid">
        <article className="content-card">
          <header className="content-card-header">
            <div>
              <span className="card-kicker">
                Distribución
              </span>

              <h2>
                Estado de documentos
              </h2>

              <p>
                Resultado actual del flujo
                de procesamiento.
              </p>
            </div>
          </header>

          <div className="chart-container">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <PieChart>
                <Pie
                  data={statusData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={72}
                  outerRadius={106}
                  paddingAngle={4}
                >
                  {statusData.map(
                    (item) => (
                      <Cell
                        key={item.status}
                        fill={
                          statusColors[
                            item.status
                          ] || "#7A7770"
                        }
                      />
                    ),
                  )}
                </Pie>

                <Tooltip
                  formatter={(value) => [
                    formatNumber(value),
                    "Facturas",
                  ]}
                />

                <Legend
                  iconType="circle"
                  wrapperStyle={{
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="content-card">
          <header className="content-card-header">
            <div>
              <span className="card-kicker">
                Proveedores
              </span>

              <h2>
                Monto procesado
              </h2>

              <p>
                Totales acumulados por
                proveedor.
              </p>
            </div>
          </header>

          <div className="chart-container">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <BarChart
                data={providerData}
                margin={{
                  top: 10,
                  right: 10,
                  left: 5,
                  bottom: 45,
                }}
              >
                <CartesianGrid
                  strokeDasharray="4 4"
                  vertical={false}
                  stroke="#E6E2D9"
                />

                <XAxis
                  dataKey="name"
                  angle={-18}
                  textAnchor="end"
                  interval={0}
                  height={90}
                  tick={{
                    fontSize: 11,
                    fill: "#77746D",
                  }}
                  axisLine={false}
                  tickLine={false}
                />

                <YAxis
                  tickFormatter={(value) =>
                    `Q${value}`
                  }
                  tick={{
                    fontSize: 11,
                    fill: "#77746D",
                  }}
                  axisLine={false}
                  tickLine={false}
                />

                <Tooltip
                  formatter={(value) => [
                    formatCurrency(value),
                    "Total",
                  ]}
                />

                <Bar
                  dataKey="total"
                  radius={[9, 9, 0, 0]}
                  maxBarSize={54}
                >
                  {providerData.map(
                    (provider, index) => (
                      <Cell
                        key={
                          `provider-${provider.name}`
                        }
                        fill={
                          providerColors[
                            index %
                              providerColors.length
                          ]
                        }
                      />
                    ),
                  )}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="content-card operational-card">
        <header className="content-card-header">
          <div>
            <span className="card-kicker">
              Operación
            </span>

            <h2>
              Estado complementario
            </h2>
          </div>
        </header>

        <div className="operational-grid">
          <article>
            <span>Pendientes</span>
            <strong>
              {formatNumber(
                summary.pending_invoices,
              )}
            </strong>
          </article>

          <article>
            <span>Procesando</span>
            <strong>
              {formatNumber(
                summary.processing_invoices,
              )}
            </strong>
          </article>

          <article>
            <span>Rechazadas</span>
            <strong>
              {formatNumber(
                summary.rejected_invoices,
              )}
            </strong>
          </article>

          <article>
            <span>Con error</span>
            <strong>
              {formatNumber(
                summary.error_invoices,
              )}
            </strong>
          </article>

          <article>
            <span>Duplicadas</span>
            <strong>
              {formatNumber(
                summary.duplicate_invoices,
              )}
            </strong>
          </article>

          <article>
            <span>IVA procesado</span>
            <strong>
              {formatCurrency(
                summary.processed_tax,
              )}
            </strong>
          </article>
        </div>
      </section>
    </div>
  );
}
