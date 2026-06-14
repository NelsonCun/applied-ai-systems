export function LoadingState({
  message = "Cargando información...",
}) {
  return (
    <div className="state-box">
      <span className="spinner" />
      <p>{message}</p>
    </div>
  );
}


export function EmptyState({
  title,
  description,
  action = null,
}) {
  return (
    <div className="empty-state">
      <div className="empty-symbol">SB</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}


export function ErrorBox({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div className="alert alert-error">
      {message}
    </div>
  );
}


export function StatusBadge({
  active,
  activeLabel = "Activo",
  inactiveLabel = "Inactivo",
}) {
  return (
    <span
      className={
        active
          ? "badge badge-success"
          : "badge badge-neutral"
      }
    >
      {active ? activeLabel : inactiveLabel}
    </span>
  );
}


export function AnswerBadge({ answered }) {
  return (
    <span
      className={
        answered
          ? "badge badge-info"
          : "badge badge-warning"
      }
    >
      {answered ? "Respondida" : "Sin respuesta"}
    </span>
  );
}
