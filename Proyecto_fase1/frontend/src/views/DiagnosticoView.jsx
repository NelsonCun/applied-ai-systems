import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BatteryCharging,
  Bot,
  CheckCircle2,
  Clock,
  Cpu,
  HardDrive,
  History,
  Keyboard,
  Loader2,
  Monitor,
  MousePointer2,
  Network,
  RefreshCcw,
  Send,
  Server,
  ShieldCheck,
  Terminal,
  Thermometer,
  Volume2,
  Wifi,
  Wrench,
  Zap,
} from "lucide-react";

import { diagnosticarSintomas } from "../services/api";

const GRUPOS_META = {
  "Arranque y energía": {
    icon: Zap,
    descripcion: "Encendido, carga, pantalla inicial y energía.",
  },
  "Sistema operativo": {
    icon: Monitor,
    descripcion: "Errores del sistema, lentitud y comportamiento anómalo.",
  },
  "Hardware interno": {
    icon: Cpu,
    descripcion: "Memoria, almacenamiento, temperatura y componentes físicos.",
  },
  Conectividad: {
    icon: Wifi,
    descripcion: "Red, puertos, audio y dispositivos externos.",
  },
  Periféricos: {
    icon: Keyboard,
    descripcion: "Entrada, reloj del sistema y dispositivos básicos.",
  },
  Otros: {
    icon: Wrench,
    descripcion: "Síntomas adicionales del equipo.",
  },
};

const ICONOS_SINTOMA = {
  no_enciende: Zap,
  pantalla_negra: Monitor,
  bateria_no_carga: BatteryCharging,
  pantalla_azul: AlertTriangle,
  lentitud_sistema: Activity,
  aplicaciones_se_cierran: Terminal,
  ventanas_emergentes: ShieldCheck,
  reinicio_inesperado: RefreshCcw,
  pitidos_arranque: Activity,
  ruido_disco: HardDrive,
  sobrecalentamiento: Thermometer,
  ventilador_ruidoso: Cpu,
  sin_internet: Network,
  no_detecta_usb: Server,
  sin_sonido: Volume2,
  teclado_no_responde: Keyboard,
  mouse_no_responde: MousePointer2,
  fecha_hora_reinicia: Clock,
};

function obtenerNivelConfianza(coincidencias) {
  if (coincidencias >= 3) {
    return {
      texto: "Alta",
      clase: "alta",
      descripcion: "Coincidencia fuerte con los síntomas registrados.",
    };
  }

  if (coincidencias === 2) {
    return {
      texto: "Media",
      clase: "media",
      descripcion: "Coincidencia parcial con un diagnóstico conocido.",
    };
  }

  return {
    texto: "Baja",
    clase: "baja",
    descripcion: "Resultado preliminar con evidencia limitada.",
  };
}

function obtenerMensajeError(error) {
  const detalle = error.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

  if (error.code === "ECONNABORTED") {
    return "El diagnóstico está tardando más de lo esperado.";
  }

  if (error.request) {
    return "No se recibió respuesta del servidor.";
  }

  return "No fue posible realizar el diagnóstico.";
}

function DiagnosticoView({ sintomas, onHistorialActualizado }) {
  const [seleccionados, setSeleccionados] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const sintomasPorId = useMemo(
    () => Object.fromEntries(sintomas.map((item) => [item.id, item.nombre])),
    [sintomas],
  );

  const sintomasAgrupados = useMemo(() => {
    const grupos = {};

    sintomas.forEach((sintoma) => {
      const grupo = sintoma.categoria || "Otros";

      if (!grupos[grupo]) grupos[grupo] = [];
      grupos[grupo].push(sintoma);
    });

    return Object.entries(grupos).map(([grupo, items]) => ({
      grupo,
      sintomas: items,
      ...(GRUPOS_META[grupo] || GRUPOS_META.Otros),
    }));
  }, [sintomas]);

  const confianza = resultado
    ? obtenerNivelConfianza(resultado.coincidencias)
    : null;

  function nombreSintoma(id) {
    return sintomasPorId[id] || id.replaceAll("_", " ");
  }

  function alternarSintoma(id) {
    setSeleccionados((actuales) =>
      actuales.includes(id)
        ? actuales.filter((item) => item !== id)
        : [...actuales, id],
    );
  }

  function reiniciarConsulta() {
    setSeleccionados([]);
    setResultado(null);
    setError("");
  }

  async function solicitarDiagnostico() {
    if (seleccionados.length === 0) {
      setError("Seleccione al menos un síntoma para continuar.");
      return;
    }

    setCargando(true);
    setError("");
    setResultado(null);

    try {
      const data = await diagnosticarSintomas(seleccionados);
      setResultado(data);

      try {
        await onHistorialActualizado();
      } catch (historialError) {
        console.error("No se pudo actualizar el historial:", historialError);
        setError(
          "El diagnóstico fue generado, pero no se pudo actualizar el historial.",
        );
      }
    } catch (diagnosticoError) {
      console.error("Error al solicitar diagnóstico:", diagnosticoError);
      setError(obtenerMensajeError(diagnosticoError));
    } finally {
      setCargando(false);
    }
  }

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Diagnóstico asistido</p>
          <h1>Identifique fallas comunes de forma rápida y guiada.</h1>
          <p className="hero-text">
            Seleccione lo que observa en el equipo y reciba un diagnóstico
            preliminar acompañado de una recomendación clara.
          </p>

          <div className="hero-actions">
            <a className="primary-link" href="#seleccion-sintomas">
              Iniciar diagnóstico
            </a>
            <button
              type="button"
              className="secondary-link"
              onClick={reiniciarConsulta}
            >
              Reiniciar consulta
            </button>
          </div>
        </div>

        <div className="status-board">
          <div className="status-card">
            <Activity size={24} />
            <span>Proceso</span>
            <strong>Evaluación guiada</strong>
          </div>
          <div className="status-card">
            <Wrench size={24} />
            <span>Resultado</span>
            <strong>Recomendación clara</strong>
          </div>
          <div className="status-card">
            <Bot size={24} />
            <span>Aviso</span>
            <strong>Notificación automática</strong>
          </div>
          <div className="status-card">
            <History size={24} />
            <span>Seguimiento</span>
            <strong>Registro de consultas</strong>
          </div>
        </div>
      </section>

      <section className="feature-grid" aria-label="Ventajas del sistema">
        <article className="feature-card">
          <ShieldCheck size={31} />
          <div>
            <h3>Evaluación ordenada</h3>
            <p>Los síntomas se agrupan por áreas para facilitar la selección.</p>
          </div>
        </article>
        <article className="feature-card">
          <Activity size={31} />
          <div>
            <h3>Resultado preliminar</h3>
            <p>Se presenta la falla probable según los síntomas elegidos.</p>
          </div>
        </article>
        <article className="feature-card">
          <History size={31} />
          <div>
            <h3>Seguimiento</h3>
            <p>Cada consulta puede revisarse posteriormente en el historial.</p>
          </div>
        </article>
      </section>

      {error && (
        <div className="notice error" role="alert">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      <section id="seleccion-sintomas" className="diagnostic-layout">
        <div className="panel main-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Selección</p>
              <h2>¿Qué síntomas presenta el equipo?</h2>
            </div>

            <button type="button" className="ghost-button" onClick={reiniciarConsulta}>
              <RefreshCcw size={17} />
              Limpiar
            </button>
          </div>

          <div className="symptom-groups">
            {sintomasAgrupados.map((grupo) => {
              const GroupIcon = grupo.icon;

              return (
                <article className="symptom-group" key={grupo.grupo}>
                  <div className="group-header">
                    <span className="group-icon">
                      <GroupIcon size={22} />
                    </span>
                    <div>
                      <h3>{grupo.grupo}</h3>
                      <p>{grupo.descripcion}</p>
                    </div>
                  </div>

                  <div className="symptom-list">
                    {grupo.sintomas.map((sintoma) => {
                      const seleccionado = seleccionados.includes(sintoma.id);
                      const SymptomIcon = ICONOS_SINTOMA[sintoma.id] || Wrench;

                      return (
                        <button
                          type="button"
                          key={sintoma.id}
                          className={seleccionado ? "symptom selected" : "symptom"}
                          onClick={() => alternarSintoma(sintoma.id)}
                          aria-pressed={seleccionado}
                        >
                          <SymptomIcon size={18} />
                          <span>{sintoma.nombre}</span>
                          {seleccionado && <CheckCircle2 size={18} className="check" />}
                        </button>
                      );
                    })}
                  </div>
                </article>
              );
            })}
          </div>
        </div>

        <aside className="panel side-panel">
          <p className="eyebrow">Resumen</p>
          <h2>{seleccionados.length} síntomas seleccionados</h2>
          <p className="muted">
            Elija únicamente los síntomas que realmente observa en el equipo.
          </p>

          <div className="selected-list">
            {seleccionados.length === 0 ? (
              <span className="empty-state">Aún no ha seleccionado síntomas.</span>
            ) : (
              seleccionados.map((id) => (
                <span className="selected-chip" key={id}>
                  {nombreSintoma(id)}
                </span>
              ))
            )}
          </div>

          <button
            type="button"
            className="diagnose-button"
            onClick={solicitarDiagnostico}
            disabled={cargando || seleccionados.length === 0}
          >
            {cargando ? (
              <>
                <Loader2 size={18} className="spin" />
                Analizando...
              </>
            ) : (
              <>
                <Send size={18} />
                Solicitar diagnóstico
              </>
            )}
          </button>
        </aside>
      </section>

      {resultado && (
        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p className="eyebrow">Resultado</p>
              <h2>{resultado.falla_texto}</h2>
            </div>

            <div className={`confidence ${confianza.clase}`}>
              <span>Confianza</span>
              <strong>{confianza.texto}</strong>
            </div>
          </div>

          <div className="result-grid">
            <article className="metric-card">
              <span>Coincidencias</span>
              <strong>{resultado.coincidencias}</strong>
              <small>{confianza.descripcion}</small>
            </article>
            <article className="metric-card">
              <span>Notificación</span>
              <strong>{resultado.telegram_enviado ? "Enviada" : "No enviada"}</strong>
              <small>
                {resultado.telegram_enviado
                  ? "El resultado fue enviado correctamente."
                  : "La notificación está desactivada o sin configurar."}
              </small>
            </article>
            <article className="metric-card">
              <span>Síntomas evaluados</span>
              <strong>{resultado.sintomas.length}</strong>
              <small>Datos utilizados para obtener el resultado.</small>
            </article>
          </div>

          <div className="recommendation">
            <span className="recommendation-icon">
              <Wrench size={24} />
            </span>
            <div>
              <h3>Recomendación</h3>
              <p>{resultado.recomendacion}</p>
            </div>
          </div>

          <div className="evaluated">
            {resultado.sintomas.map((id) => (
              <span key={id}>{nombreSintoma(id)}</span>
            ))}
          </div>
        </section>
      )}
    </>
  );
}

export default DiagnosticoView;
