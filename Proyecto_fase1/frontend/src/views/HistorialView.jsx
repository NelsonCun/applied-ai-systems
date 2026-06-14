import { useMemo, useState } from "react";
import {
  AlertTriangle,
  History,
  RefreshCcw,
  Trash2,
} from "lucide-react";

function HistorialView({ historial, sintomas, onRecargar, onLimpiar }) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const sintomasPorId = useMemo(
    () => Object.fromEntries(sintomas.map((item) => [item.id, item.nombre])),
    [sintomas],
  );

  function nombreSintoma(id) {
    return sintomasPorId[id] || id.replaceAll("_", " ");
  }

  async function recargar() {
    setCargando(true);
    setError("");

    try {
      await onRecargar();
    } catch (recargaError) {
      console.error("No se pudo recargar el historial:", recargaError);
      setError("No se pudo actualizar el historial.");
    } finally {
      setCargando(false);
    }
  }

  async function limpiar() {
    const confirmado = window.confirm(
      "¿Desea eliminar todo el historial de diagnósticos?",
    );

    if (!confirmado) return;

    setCargando(true);
    setError("");

    try {
      await onLimpiar();
    } catch (limpiezaError) {
      console.error("No se pudo limpiar el historial:", limpiezaError);
      setError("No se pudo eliminar el historial.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="panel history-panel standalone-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Seguimiento</p>
          <h1 className="view-title">Historial de diagnósticos</h1>
          <p className="view-description">
            Consulte los resultados generados anteriormente y los síntomas que
            fueron evaluados en cada caso.
          </p>
        </div>

        <div className="heading-actions">
          <button type="button" className="ghost-button" onClick={recargar} disabled={cargando}>
            <RefreshCcw size={17} className={cargando ? "spin" : ""} />
            Actualizar
          </button>
          <button type="button" className="ghost-button danger" onClick={limpiar} disabled={cargando}>
            <Trash2 size={17} />
            Limpiar historial
          </button>
        </div>
      </div>

      {error && (
        <div className="notice error" role="alert">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {historial.length === 0 ? (
        <div className="history-empty">
          <History size={38} />
          <h3>Sin diagnósticos registrados</h3>
          <p>Los resultados aparecerán aquí después de realizar una consulta.</p>
        </div>
      ) : (
        <div className="history-list">
          {historial.map((item) => (
            <article className="history-item" key={item.id}>
              <div>
                <span className="history-date">{item.fecha}</span>
                <h3>{item.falla_texto}</h3>
                <p>{item.recomendacion}</p>
              </div>

              <div className="history-meta">
                <span>{item.coincidencias} coincidencias</span>
                <span>
                  {item.telegram_enviado
                    ? "Notificación enviada"
                    : "Notificación no enviada"}
                </span>
              </div>

              <div className="history-symptoms">
                {item.sintomas.map((id) => (
                  <span key={`${item.id}-${id}`}>{nombreSintoma(id)}</span>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default HistorialView;
