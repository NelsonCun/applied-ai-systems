const labels = {
  ACTIVE: "Activo",
  INACTIVE: "Inactivo",
  PENDING: "Pendiente",
  PROCESSING: "Procesando",
  PROCESSED: "Procesada",
  REJECTED: "Rechazada",
  ERROR: "Error",
  DUPLICATE: "Duplicada",
  SUCCESS: "Correcto",
  RUNNING: "En ejecución",
};


export default function StatusBadge({
  status,
}) {
  const normalized = String(
    status || "",
  ).toUpperCase();

  return (
    <span
      className={[
        "status-badge",
        `status-${normalized.toLowerCase()}`,
      ].join(" ")}
    >
      {labels[normalized] || normalized}
    </span>
  );
}
