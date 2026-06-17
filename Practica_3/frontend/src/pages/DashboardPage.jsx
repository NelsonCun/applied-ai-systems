import {
  AlertTriangle,
  CheckCircle2,
  CircleDollarSign,
  FileClock,
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

const chartColors = [
  "#2563eb",
  "#16a34a",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
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
          total: Number(
            item.total_amount || 0,
          ),
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
          facturas:
            provider.invoice_count,
          total: Number(
            provider.total_amount,
          ),
        })),
    [dashboard],
  );


  if (loading) {
    return (
      <section className="page-state">
        <LoaderCircle
          className="spin"
          size={32}
        />

        <p>Cargando indicadores...</p>
      </section>
    );
  }


  if (error) {
    return (
      <section className="page-state">
        <AlertTriangle size={34} />

        <h2>No se pudo cargar el dashboard</h2>

        <p>{error}</p>

        <button
          className="secondary-button"
          type="button"
          onClick={loadDashboard}
        >
          <RefreshCw size={18} />
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
      label: "Facturas procesadas",
      value: formatNumber(
        summary.processed_invoices,
      ),
      detail: "Procesamiento completado",
      icon: CheckCircle2,
      variant: "green",
    },
    {
      label: "Monto procesado",
      value: formatCurrency(
        summary.processed_total,
      ),
      detail: "Total acumulado",
      icon: CircleDollarSign,
      variant: "purple",
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
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Resumen administrativo
          </p>

          <h1>Dashboard</h1>

          <p>
            Estado general del procesamiento
            y administración de facturas.
          </p>
        </div>

        <button
          className="secondary-button"
          type="button"
          onClick={loadDashboard}
        >
          <RefreshCw size={18} />
          Actualizar
        </button>
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
              className="metric-card"
              key={label}
            >
              <div
                className={
                  `metric-icon metric-${variant}`
                }
              >
                <Icon size={23} />
              </div>

              <div className="metric-copy">
                <span>{label}</span>
                <strong>{value}</strong>
                <small>{detail}</small>
              </div>
            </article>
          ),
        )}
      </section>

      <section className="dashboard-grid">
        <article className="content-card">
          <header className="content-card-header">
            <div>
              <h2>Distribución por estado</h2>

              <p>
                Cantidad de documentos por
                resultado del procesamiento.
              </p>
            </div>
          </header>

          <div className="chart-container">
            {statusData.length > 0 ? (
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={66}
                    outerRadius={102}
                    paddingAngle={3}
                  >
                    {statusData.map(
                      (_, index) => (
                        <Cell
                          key={index}
                          fill={
                            chartColors[
                              index %
                                chartColors.length
                            ]
                          }
                        />
                      ),
                    )}
                  </Pie>

                  <Tooltip
                    formatter={(
                      value,
                      name,
                    ) => [
                      formatNumber(value),
                      name,
                    ]}
                  />

                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <FileClock size={30} />
                <p>
                  No existen facturas
                  registradas.
                </p>
              </div>
            )}
          </div>
        </article>

        <article className="content-card">
          <header className="content-card-header">
            <div>
              <h2>Totales por proveedor</h2>

              <p>
                Valor procesado de los
                principales proveedores.
              </p>
            </div>
          </header>

          <div className="chart-container">
            {providerData.length > 0 ? (
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <BarChart
                  data={providerData}
                  margin={{
                    top: 10,
                    right: 15,
                    left: 10,
                    bottom: 35,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="name"
                    angle={-18}
                    textAnchor="end"
                    interval={0}
                    height={80}
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    tickFormatter={(value) =>
                      `Q${value}`
                    }
                  />

                  <Tooltip
                    formatter={(value) => [
                      formatCurrency(value),
                      "Total",
                    ]}
                  />

                  <Bar
                    dataKey="total"
                    name="Total"
                    fill="#2563eb"
                    radius={[7, 7, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <CircleDollarSign
                  size={30}
                />

                <p>
                  No existen montos para
                  mostrar.
                </p>
              </div>
            )}
          </div>
        </article>
      </section>

      <section className="content-card">
        <header className="content-card-header">
          <div>
            <h2>Resumen operativo</h2>

            <p>
              Indicadores complementarios
              del procesamiento documental.
            </p>
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
            <span>En procesamiento</span>
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
