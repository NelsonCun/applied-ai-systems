import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Cpu,
  Edit3,
  GitBranch,
  LayoutDashboard,
  Lightbulb,
  Loader2,
  RefreshCcw,
  Save,
  Settings,
  Trash2,
  Wrench,
  X,
} from "lucide-react";

import {
  actualizarConfiguracionTelegram,
  actualizarFalla,
  actualizarRecomendacion,
  actualizarRegla,
  actualizarSintoma,
  crearFalla,
  crearRecomendacion,
  crearRegla,
  crearSintoma,
  eliminarFalla,
  eliminarRecomendacion,
  eliminarRegla,
  eliminarSintoma,
  obtenerDatosAdministracion,
  obtenerDetalleError,
} from "../services/api";

const SECCIONES = [
  { id: "resumen", etiqueta: "Resumen", icono: LayoutDashboard },
  { id: "sintomas", etiqueta: "Síntomas", icono: Cpu },
  { id: "fallas", etiqueta: "Fallas", icono: Wrench },
  { id: "recomendaciones", etiqueta: "Recomendaciones", icono: Lightbulb },
  { id: "reglas", etiqueta: "Reglas", icono: GitBranch },
  { id: "configuracion", etiqueta: "Configuración", icono: Settings },
];

const FORMULARIOS_INICIALES = {
  sintoma: { id: "", nombre: "", categoria: "" },
  falla: { id: "", nombre: "", descripcion: "" },
  recomendacion: { id: "", falla_id: "", texto: "" },
  regla: { id: "", falla_id: "", sintomas: [] },
};

function MensajeEstado({ mensaje }) {
  if (!mensaje.texto) return null;

  return (
    <div className={`notice ${mensaje.tipo}`} role="status">
      {mensaje.tipo === "success" ? (
        <CheckCircle2 size={20} />
      ) : (
        <AlertTriangle size={20} />
      )}
      <span>{mensaje.texto}</span>
    </div>
  );
}

function BotonesFila({ onEditar, onEliminar }) {
  return (
    <div className="row-actions">
      <button type="button" className="icon-button" onClick={onEditar} title="Editar">
        <Edit3 size={16} />
      </button>
      <button
        type="button"
        className="icon-button danger"
        onClick={onEliminar}
        title="Eliminar"
      >
        <Trash2 size={16} />
      </button>
    </div>
  );
}

function ResumenAdmin({ datos }) {
  const recomendacionesPorFalla = useMemo(
    () =>
      Object.fromEntries(
        datos.recomendaciones.map((item) => [item.falla_id, item]),
      ),
    [datos.recomendaciones],
  );

  const sintomasPorId = useMemo(
    () => Object.fromEntries(datos.sintomas.map((item) => [item.id, item.nombre])),
    [datos.sintomas],
  );

  return (
    <div className="admin-section-stack">
      <div className="admin-metrics">
        <article className="admin-metric">
          <span>Síntomas</span>
          <strong>{datos.sintomas.length}</strong>
          <small>Mínimo requerido: 15</small>
        </article>
        <article className="admin-metric">
          <span>Fallas</span>
          <strong>{datos.fallas.length}</strong>
          <small>Mínimo requerido: 10</small>
        </article>
        <article className="admin-metric">
          <span>Recomendaciones</span>
          <strong>{datos.recomendaciones.length}</strong>
          <small>Mínimo requerido: 10</small>
        </article>
        <article className="admin-metric">
          <span>Reglas</span>
          <strong>{datos.reglas.length}</strong>
          <small>Mínimo requerido: 10</small>
        </article>
      </div>

      <section className="admin-card">
        <div className="admin-card-header">
          <div>
            <p className="eyebrow">Asociaciones</p>
            <h3>Síntomas, fallas y recomendaciones</h3>
          </div>
        </div>

        <div className="association-list">
          {datos.reglas.map((regla) => {
            const recomendacion = recomendacionesPorFalla[regla.falla_id];

            return (
              <article className="association-card" key={regla.id}>
                <div className="association-column">
                  <span className="association-label">Síntomas</span>
                  <div className="tag-list">
                    {regla.sintomas.map((id) => (
                      <span className="tag" key={id}>
                        {sintomasPorId[id] || id}
                      </span>
                    ))}
                  </div>
                </div>

                <span className="association-arrow">→</span>

                <div className="association-column">
                  <span className="association-label">Falla</span>
                  <strong>{regla.falla_nombre}</strong>
                </div>

                <span className="association-arrow">→</span>

                <div className="association-column">
                  <span className="association-label">Recomendación</span>
                  <p>{recomendacion?.texto || "Sin recomendación asociada"}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}

function SintomasAdmin({ items, onRecargar, onConocimientoActualizado, setMensaje }) {
  const [formulario, setFormulario] = useState(FORMULARIOS_INICIALES.sintoma);
  const [editando, setEditando] = useState(null);
  const [guardando, setGuardando] = useState(false);

  function cancelar() {
    setFormulario(FORMULARIOS_INICIALES.sintoma);
    setEditando(null);
  }

  function editar(item) {
    setEditando(item.id);
    setFormulario({ ...item });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function guardar(evento) {
    evento.preventDefault();
    setGuardando(true);
    setMensaje({ tipo: "", texto: "" });

    try {
      if (editando) {
        await actualizarSintoma(editando, {
          nombre: formulario.nombre,
          categoria: formulario.categoria,
        });
      } else {
        await crearSintoma(formulario);
      }

      await onRecargar();
      await onConocimientoActualizado();
      cancelar();
      setMensaje({ tipo: "success", texto: "Síntoma guardado correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setGuardando(false);
    }
  }

  async function eliminar(id) {
    if (!window.confirm(`¿Desea eliminar el síntoma '${id}'?`)) return;

    try {
      await eliminarSintoma(id);
      await onRecargar();
      await onConocimientoActualizado();
      setMensaje({ tipo: "success", texto: "Síntoma eliminado correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    }
  }

  return (
    <div className="admin-split">
      <form className="admin-card admin-form" onSubmit={guardar}>
        <div className="admin-card-header">
          <div>
            <p className="eyebrow">{editando ? "Edición" : "Nuevo registro"}</p>
            <h3>{editando ? "Editar síntoma" : "Crear síntoma"}</h3>
          </div>
          {editando && (
            <button type="button" className="icon-button" onClick={cancelar}>
              <X size={17} />
            </button>
          )}
        </div>

        <label className="form-field">
          <span>Identificador</span>
          <input
            value={formulario.id}
            disabled={Boolean(editando)}
            onChange={(evento) =>
              setFormulario({ ...formulario, id: evento.target.value })
            }
            placeholder="ejemplo_sintoma"
            required
          />
        </label>

        <label className="form-field">
          <span>Nombre visible</span>
          <input
            value={formulario.nombre}
            onChange={(evento) =>
              setFormulario({ ...formulario, nombre: evento.target.value })
            }
            placeholder="Descripción para el usuario"
            required
          />
        </label>

        <label className="form-field">
          <span>Categoría</span>
          <input
            value={formulario.categoria}
            onChange={(evento) =>
              setFormulario({ ...formulario, categoria: evento.target.value })
            }
            placeholder="Hardware interno"
            required
          />
        </label>

        <button type="submit" className="primary-button" disabled={guardando}>
          {guardando ? <Loader2 size={17} className="spin" /> : <Save size={17} />}
          {editando ? "Guardar cambios" : "Crear síntoma"}
        </button>
      </form>

      <section className="admin-card admin-list-card">
        <div className="admin-card-header">
          <div>
            <p className="eyebrow">Registros</p>
            <h3>Síntomas disponibles</h3>
          </div>
          <span className="count-badge">{items.length}</span>
        </div>

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Identificador</th>
                <th>Nombre</th>
                <th>Categoría</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td><code>{item.id}</code></td>
                  <td>{item.nombre}</td>
                  <td>{item.categoria}</td>
                  <td>
                    <BotonesFila onEditar={() => editar(item)} onEliminar={() => eliminar(item.id)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function FallasAdmin({ items, onRecargar, setMensaje }) {
  const [formulario, setFormulario] = useState(FORMULARIOS_INICIALES.falla);
  const [editando, setEditando] = useState(null);
  const [guardando, setGuardando] = useState(false);

  function cancelar() {
    setFormulario(FORMULARIOS_INICIALES.falla);
    setEditando(null);
  }

  function editar(item) {
    setEditando(item.id);
    setFormulario({ ...item });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function guardar(evento) {
    evento.preventDefault();
    setGuardando(true);
    setMensaje({ tipo: "", texto: "" });

    try {
      if (editando) {
        await actualizarFalla(editando, {
          nombre: formulario.nombre,
          descripcion: formulario.descripcion,
        });
      } else {
        await crearFalla(formulario);
      }

      await onRecargar();
      cancelar();
      setMensaje({ tipo: "success", texto: "Falla guardada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setGuardando(false);
    }
  }

  async function eliminar(id) {
    if (!window.confirm(`¿Desea eliminar la falla '${id}'?`)) return;

    try {
      await eliminarFalla(id);
      await onRecargar();
      setMensaje({ tipo: "success", texto: "Falla eliminada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    }
  }

  return (
    <div className="admin-split">
      <form className="admin-card admin-form" onSubmit={guardar}>
        <div className="admin-card-header">
          <div>
            <p className="eyebrow">{editando ? "Edición" : "Nuevo registro"}</p>
            <h3>{editando ? "Editar falla" : "Crear falla"}</h3>
          </div>
          {editando && (
            <button type="button" className="icon-button" onClick={cancelar}>
              <X size={17} />
            </button>
          )}
        </div>

        <label className="form-field">
          <span>Identificador</span>
          <input
            value={formulario.id}
            disabled={Boolean(editando)}
            onChange={(evento) => setFormulario({ ...formulario, id: evento.target.value })}
            placeholder="falla_ejemplo"
            required
          />
        </label>
        <label className="form-field">
          <span>Nombre visible</span>
          <input
            value={formulario.nombre}
            onChange={(evento) => setFormulario({ ...formulario, nombre: evento.target.value })}
            required
          />
        </label>
        <label className="form-field">
          <span>Descripción</span>
          <textarea
            rows="5"
            value={formulario.descripcion}
            onChange={(evento) => setFormulario({ ...formulario, descripcion: evento.target.value })}
            required
          />
        </label>
        <button type="submit" className="primary-button" disabled={guardando}>
          {guardando ? <Loader2 size={17} className="spin" /> : <Save size={17} />}
          {editando ? "Guardar cambios" : "Crear falla"}
        </button>
      </form>

      <section className="admin-card admin-list-card">
        <div className="admin-card-header">
          <div><p className="eyebrow">Registros</p><h3>Fallas diagnosticables</h3></div>
          <span className="count-badge">{items.length}</span>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Identificador</th><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td><code>{item.id}</code></td>
                  <td>{item.nombre}</td>
                  <td>{item.descripcion}</td>
                  <td><BotonesFila onEditar={() => editar(item)} onEliminar={() => eliminar(item.id)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function RecomendacionesAdmin({ items, fallas, onRecargar, setMensaje }) {
  const [formulario, setFormulario] = useState(FORMULARIOS_INICIALES.recomendacion);
  const [editando, setEditando] = useState(null);
  const [guardando, setGuardando] = useState(false);

  function cancelar() {
    setFormulario(FORMULARIOS_INICIALES.recomendacion);
    setEditando(null);
  }

  function editar(item) {
    setEditando(item.id);
    setFormulario({ id: item.id, falla_id: item.falla_id, texto: item.texto });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function guardar(evento) {
    evento.preventDefault();
    setGuardando(true);
    setMensaje({ tipo: "", texto: "" });

    try {
      if (editando) {
        await actualizarRecomendacion(editando, {
          falla_id: formulario.falla_id,
          texto: formulario.texto,
        });
      } else {
        await crearRecomendacion(formulario);
      }

      await onRecargar();
      cancelar();
      setMensaje({ tipo: "success", texto: "Recomendación guardada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setGuardando(false);
    }
  }

  async function eliminar(id) {
    if (!window.confirm(`¿Desea eliminar la recomendación '${id}'?`)) return;

    try {
      await eliminarRecomendacion(id);
      await onRecargar();
      setMensaje({ tipo: "success", texto: "Recomendación eliminada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    }
  }

  return (
    <div className="admin-split">
      <form className="admin-card admin-form" onSubmit={guardar}>
        <div className="admin-card-header">
          <div><p className="eyebrow">{editando ? "Edición" : "Nuevo registro"}</p><h3>{editando ? "Editar recomendación" : "Crear recomendación"}</h3></div>
          {editando && <button type="button" className="icon-button" onClick={cancelar}><X size={17} /></button>}
        </div>
        <label className="form-field">
          <span>Identificador</span>
          <input value={formulario.id} disabled={Boolean(editando)} onChange={(evento) => setFormulario({ ...formulario, id: evento.target.value })} placeholder="rec_ejemplo" required />
        </label>
        <label className="form-field">
          <span>Falla asociada</span>
          <select value={formulario.falla_id} onChange={(evento) => setFormulario({ ...formulario, falla_id: evento.target.value })} required>
            <option value="">Seleccione una falla</option>
            {fallas.map((falla) => <option key={falla.id} value={falla.id}>{falla.nombre}</option>)}
          </select>
        </label>
        <label className="form-field">
          <span>Texto de la recomendación</span>
          <textarea rows="7" value={formulario.texto} onChange={(evento) => setFormulario({ ...formulario, texto: evento.target.value })} required />
        </label>
        <button type="submit" className="primary-button" disabled={guardando}>
          {guardando ? <Loader2 size={17} className="spin" /> : <Save size={17} />}
          {editando ? "Guardar cambios" : "Crear recomendación"}
        </button>
      </form>

      <section className="admin-card admin-list-card">
        <div className="admin-card-header"><div><p className="eyebrow">Registros</p><h3>Recomendaciones</h3></div><span className="count-badge">{items.length}</span></div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Identificador</th><th>Falla</th><th>Recomendación</th><th>Acciones</th></tr></thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td><code>{item.id}</code></td>
                  <td>{item.falla_nombre}</td>
                  <td>{item.texto}</td>
                  <td><BotonesFila onEditar={() => editar(item)} onEliminar={() => eliminar(item.id)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ReglasAdmin({ items, fallas, sintomas, onRecargar, setMensaje }) {
  const [formulario, setFormulario] = useState(FORMULARIOS_INICIALES.regla);
  const [editando, setEditando] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const sintomasPorId = useMemo(
    () => Object.fromEntries(sintomas.map((item) => [item.id, item.nombre])),
    [sintomas],
  );

  function cancelar() {
    setFormulario(FORMULARIOS_INICIALES.regla);
    setEditando(null);
  }

  function editar(item) {
    setEditando(item.id);
    setFormulario({ id: item.id, falla_id: item.falla_id, sintomas: [...item.sintomas] });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function alternarSintoma(id) {
    setFormulario((actual) => ({
      ...actual,
      sintomas: actual.sintomas.includes(id)
        ? actual.sintomas.filter((item) => item !== id)
        : [...actual.sintomas, id],
    }));
  }

  async function guardar(evento) {
    evento.preventDefault();

    if (formulario.sintomas.length === 0) {
      setMensaje({ tipo: "error", texto: "Seleccione al menos un síntoma." });
      return;
    }

    setGuardando(true);
    setMensaje({ tipo: "", texto: "" });

    try {
      if (editando) {
        await actualizarRegla(editando, {
          falla_id: formulario.falla_id,
          sintomas: formulario.sintomas,
        });
      } else {
        await crearRegla(formulario);
      }

      await onRecargar();
      cancelar();
      setMensaje({ tipo: "success", texto: "Regla guardada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setGuardando(false);
    }
  }

  async function eliminar(id) {
    if (!window.confirm(`¿Desea eliminar la regla '${id}'?`)) return;

    try {
      await eliminarRegla(id);
      await onRecargar();
      setMensaje({ tipo: "success", texto: "Regla eliminada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    }
  }

  return (
    <div className="admin-split rules-layout">
      <form className="admin-card admin-form" onSubmit={guardar}>
        <div className="admin-card-header">
          <div><p className="eyebrow">{editando ? "Edición" : "Nueva regla"}</p><h3>{editando ? "Editar regla" : "Crear regla de diagnóstico"}</h3></div>
          {editando && <button type="button" className="icon-button" onClick={cancelar}><X size={17} /></button>}
        </div>
        <label className="form-field">
          <span>Identificador</span>
          <input value={formulario.id} disabled={Boolean(editando)} onChange={(evento) => setFormulario({ ...formulario, id: evento.target.value })} placeholder="regla_ejemplo" required />
        </label>
        <label className="form-field">
          <span>Falla diagnosticada</span>
          <select value={formulario.falla_id} onChange={(evento) => setFormulario({ ...formulario, falla_id: evento.target.value })} required>
            <option value="">Seleccione una falla</option>
            {fallas.map((falla) => <option key={falla.id} value={falla.id}>{falla.nombre}</option>)}
          </select>
        </label>

        <fieldset className="checkbox-fieldset">
          <legend>Síntomas asociados</legend>
          <div className="checkbox-grid">
            {sintomas.map((sintoma) => (
              <label className="checkbox-option" key={sintoma.id}>
                <input type="checkbox" checked={formulario.sintomas.includes(sintoma.id)} onChange={() => alternarSintoma(sintoma.id)} />
                <span>{sintoma.nombre}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <button type="submit" className="primary-button" disabled={guardando}>
          {guardando ? <Loader2 size={17} className="spin" /> : <Save size={17} />}
          {editando ? "Guardar cambios" : "Crear regla"}
        </button>
      </form>

      <section className="admin-card admin-list-card">
        <div className="admin-card-header"><div><p className="eyebrow">Registros</p><h3>Reglas existentes</h3></div><span className="count-badge">{items.length}</span></div>
        <div className="rule-list">
          {items.map((item) => (
            <article className="rule-card" key={item.id}>
              <div className="rule-card-header">
                <div><code>{item.id}</code><h4>{item.falla_nombre}</h4></div>
                <BotonesFila onEditar={() => editar(item)} onEliminar={() => eliminar(item.id)} />
              </div>
              <div className="tag-list">
                {item.sintomas.map((id) => <span className="tag" key={id}>{sintomasPorId[id] || id}</span>)}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function ConfiguracionAdmin({ configuracion, onRecargar, setMensaje }) {
  const [formulario, setFormulario] = useState(configuracion);
  const [guardando, setGuardando] = useState(false);

  async function guardar(evento) {
    evento.preventDefault();
    setGuardando(true);
    setMensaje({ tipo: "", texto: "" });

    try {
      await actualizarConfiguracionTelegram({
        activo: formulario.activo,
        chat_id: formulario.chat_id,
        mensaje_bienvenida: formulario.mensaje_bienvenida,
        encabezado_diagnostico: formulario.encabezado_diagnostico,
        mensaje_despedida: formulario.mensaje_despedida,
      });
      await onRecargar();
      setMensaje({ tipo: "success", texto: "Configuración guardada correctamente." });
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div className="configuration-grid">
      <form className="admin-card admin-form wide-form" onSubmit={guardar}>
        <div className="admin-card-header">
          <div><p className="eyebrow">Notificaciones</p><h3>Configuración de Telegram</h3></div>
          <Bot size={26} />
        </div>

        <label className="switch-field">
          <span>
            <strong>Notificaciones activas</strong>
            <small>Permite enviar el resultado después de cada diagnóstico.</small>
          </span>
          <input type="checkbox" checked={formulario.activo} onChange={(evento) => setFormulario({ ...formulario, activo: evento.target.checked })} />
        </label>

        <label className="form-field">
          <span>ID de chat</span>
          <input value={formulario.chat_id} onChange={(evento) => setFormulario({ ...formulario, chat_id: evento.target.value })} placeholder="123456789" />
        </label>
        <label className="form-field">
          <span>Mensaje de bienvenida</span>
          <textarea rows="3" value={formulario.mensaje_bienvenida} onChange={(evento) => setFormulario({ ...formulario, mensaje_bienvenida: evento.target.value })} required />
        </label>
        <label className="form-field">
          <span>Encabezado del diagnóstico</span>
          <textarea rows="3" value={formulario.encabezado_diagnostico} onChange={(evento) => setFormulario({ ...formulario, encabezado_diagnostico: evento.target.value })} required />
        </label>
        <label className="form-field">
          <span>Mensaje de despedida</span>
          <textarea rows="4" value={formulario.mensaje_despedida} onChange={(evento) => setFormulario({ ...formulario, mensaje_despedida: evento.target.value })} required />
        </label>

        <button type="submit" className="primary-button" disabled={guardando}>
          {guardando ? <Loader2 size={17} className="spin" /> : <Save size={17} />}
          Guardar configuración
        </button>
      </form>

      <aside className="admin-card config-status-card">
        <p className="eyebrow">Estado</p>
        <h3>Conexión del bot</h3>
        <div className="config-status-row"><span>Token</span><strong className={formulario.token_configurado ? "status-ok" : "status-error"}>{formulario.token_configurado ? "Configurado" : "Pendiente"}</strong></div>
        <div className="config-status-row"><span>ID de chat</span><strong className={formulario.chat_id ? "status-ok" : "status-error"}>{formulario.chat_id ? "Configurado" : "Pendiente"}</strong></div>
        <div className="config-status-row"><span>Envío</span><strong className={formulario.activo ? "status-ok" : "status-muted"}>{formulario.activo ? "Activo" : "Desactivado"}</strong></div>
        <p className="muted config-help">El token permanece protegido en las variables de entorno y no se muestra en esta pantalla.</p>
      </aside>
    </div>
  );
}

function AdminView({ onConocimientoActualizado }) {
  const [seccion, setSeccion] = useState("resumen");
  const [datos, setDatos] = useState({
    sintomas: [],
    fallas: [],
    recomendaciones: [],
    reglas: [],
    configuracion: {
      activo: false,
      chat_id: "",
      mensaje_bienvenida: "",
      encabezado_diagnostico: "",
      mensaje_despedida: "",
      token_configurado: false,
    },
  });
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState({ tipo: "", texto: "" });

  async function cargarDatos() {
    setCargando(true);

    try {
      const respuesta = await obtenerDatosAdministracion();
      setDatos(respuesta);
    } catch (error) {
      setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;

    obtenerDatosAdministracion()
      .then((respuesta) => {
        if (activo) setDatos(respuesta);
      })
      .catch((error) => {
        if (activo) {
          setMensaje({ tipo: "error", texto: obtenerDetalleError(error) });
        }
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, []);

  function cambiarSeccion(id) {
    setSeccion(id);
    setMensaje({ tipo: "", texto: "" });
  }

  return (
    <section className="admin-view">
      <div className="view-hero compact-hero">
        <div>
          <p className="eyebrow">Administración</p>
          <h1 className="view-title">Gestión del conocimiento</h1>
          <p className="view-description">
            Administre los síntomas, fallas, recomendaciones, reglas y opciones
            de notificación utilizadas por Doctor Byte.
          </p>
        </div>

        <button type="button" className="ghost-button" onClick={cargarDatos} disabled={cargando}>
          <RefreshCcw size={17} className={cargando ? "spin" : ""} />
          Actualizar datos
        </button>
      </div>

      <div className="admin-tabs" role="tablist" aria-label="Secciones administrativas">
        {SECCIONES.map((item) => {
          const Icono = item.icono;
          return (
            <button type="button" key={item.id} className={seccion === item.id ? "admin-tab active" : "admin-tab"} onClick={() => cambiarSeccion(item.id)}>
              <Icono size={17} />
              {item.etiqueta}
            </button>
          );
        })}
      </div>

      <MensajeEstado mensaje={mensaje} />

      {cargando ? (
        <section className="panel loading-panel"><Loader2 size={30} className="spin" /><p>Cargando información...</p></section>
      ) : (
        <>
          {seccion === "resumen" && <ResumenAdmin datos={datos} />}
          {seccion === "sintomas" && <SintomasAdmin items={datos.sintomas} onRecargar={cargarDatos} onConocimientoActualizado={onConocimientoActualizado} setMensaje={setMensaje} />}
          {seccion === "fallas" && <FallasAdmin items={datos.fallas} onRecargar={cargarDatos} setMensaje={setMensaje} />}
          {seccion === "recomendaciones" && <RecomendacionesAdmin items={datos.recomendaciones} fallas={datos.fallas} onRecargar={cargarDatos} setMensaje={setMensaje} />}
          {seccion === "reglas" && <ReglasAdmin items={datos.reglas} fallas={datos.fallas} sintomas={datos.sintomas} onRecargar={cargarDatos} setMensaje={setMensaje} />}
          {seccion === "configuracion" && (
            <ConfiguracionAdmin
              key={JSON.stringify(datos.configuracion)}
              configuracion={datos.configuracion}
              onRecargar={cargarDatos}
              setMensaje={setMensaje}
            />
          )}
        </>
      )}
    </section>
  );
}

export default AdminView;
