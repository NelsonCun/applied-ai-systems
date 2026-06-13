import { useEffect, useMemo, useState } from "react";
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
  Trash2,
  Volume2,
  Wifi,
  Wrench,
  Zap,
} from "lucide-react";

import {
  diagnosticarSintomas,
  eliminarHistorial,
  obtenerHistorial,
  obtenerSintomas,
} from "./services/api";

import "./App.css";

const SINTOMA_GRUPO = {
  no_enciende: "Arranque y energía",
  pantalla_negra: "Arranque y energía",
  bateria_no_carga: "Arranque y energía",

  pantalla_azul: "Sistema operativo",
  lentitud_sistema: "Sistema operativo",
  aplicaciones_se_cierran: "Sistema operativo",
  ventanas_emergentes: "Sistema operativo",

  reinicio_inesperado: "Hardware interno",
  pitidos_arranque: "Hardware interno",
  ruido_disco: "Hardware interno",
  sobrecalentamiento: "Hardware interno",
  ventilador_ruidoso: "Hardware interno",

  sin_internet: "Conectividad",
  no_detecta_usb: "Conectividad",
  sin_sonido: "Conectividad",

  teclado_no_responde: "Periféricos",
  mouse_no_responde: "Periféricos",
  fecha_hora_reinicia: "Periféricos",
};

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
    descripcion: "RAM, disco, temperatura y componentes físicos.",
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
      descripcion: "Coincidencia fuerte con la base de conocimiento.",
    };
  }

  if (coincidencias === 2) {
    return {
      texto: "Media",
      clase: "media",
      descripcion: "Coincidencia parcial con una regla de diagnóstico.",
    };
  }

  return {
    texto: "Baja",
    clase: "baja",
    descripcion: "Diagnóstico preliminar con poca evidencia.",
  };
}

function App() {
  const [sintomas, setSintomas] = useState([]);
  const [sintomasSeleccionados, setSintomasSeleccionados] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  const sintomasPorId = useMemo(() => {
    return Object.fromEntries(sintomas.map((sintoma) => [sintoma.id, sintoma.nombre]));
  }, [sintomas]);

  const sintomasAgrupados = useMemo(() => {
    const grupos = {};

    sintomas.forEach((sintoma) => {
      const grupo = SINTOMA_GRUPO[sintoma.id] || "Otros";

      if (!grupos[grupo]) {
        grupos[grupo] = [];
      }

      grupos[grupo].push(sintoma);
    });

    return Object.entries(grupos).map(([grupo, items]) => ({
      grupo,
      sintomas: items,
      ...GRUPOS_META[grupo],
    }));
  }, [sintomas]);

  const confianza = resultado
    ? obtenerNivelConfianza(resultado.coincidencias)
    : null;

  async function cargarDatosIniciales() {
    try {
      setError("");

      const sintomasData = await obtenerSintomas();
      const historialData = await obtenerHistorial();

      setSintomas(sintomasData);
      setHistorial([...historialData].reverse());
    } catch {
      setError("No se pudo conectar con el backend. Verifique que FastAPI esté ejecutándose.");
    }
  }

  function nombreSintoma(id) {
    return sintomasPorId[id] || id.replaceAll("_", " ");
  }

  function manejarSeleccionSintoma(idSintoma) {
    setSintomasSeleccionados((prev) => {
      if (prev.includes(idSintoma)) {
        return prev.filter((id) => id !== idSintoma);
      }

      return [...prev, idSintoma];
    });
  }

  async function manejarDiagnostico() {
    if (sintomasSeleccionados.length === 0) {
      setError("Seleccione al menos un síntoma para iniciar el diagnóstico.");
      return;
    }

    try {
      setCargando(true);
      setError("");
      setResultado(null);

      const data = await diagnosticarSintomas(sintomasSeleccionados);
      setResultado(data);

      const historialData = await obtenerHistorial();
      setHistorial([...historialData].reverse());
    } catch {
      setError("Ocurrió un error al realizar el diagnóstico.");
    } finally {
      setCargando(false);
    }
  }

  async function manejarLimpiarHistorial() {
    const confirmar = window.confirm("¿Desea eliminar todo el historial de diagnósticos?");

    if (!confirmar) return;

    try {
      await eliminarHistorial();
      setHistorial([]);
    } catch {
      setError("No se pudo eliminar el historial.");
    }
  }

  function limpiarSeleccion() {
    setSintomasSeleccionados([]);
    setResultado(null);
    setError("");
  }

  return (
    <div className="shell">
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="Doctor Byte">
          <div className="brand-mark">
            <Cpu size={26} />
          </div>

          <div>
            <span className="brand-title">Doctor Byte</span>
            <span className="brand-subtitle">Centro de diagnóstico</span>
          </div>
        </a>

        <nav className="nav">
          <a href="#diagnostico">Diagnóstico</a>
          <a href="#resultado">Resultado</a>
          <a href="#historial">Historial</a>
        </nav>
      </header>

      <main id="inicio" className="layout">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Diagnóstico asistido</p>

            <h1>
              Detecte fallas comunes en su computadora de forma rápida y guiada.
            </h1>

            <p className="hero-text">
              Seleccione los síntomas que presenta el equipo y reciba un diagnóstico
              preliminar con recomendaciones claras para tomar una mejor decisión antes
              de realizar una reparación.
            </p>

            <div className="hero-actions">
              <a className="primary-link" href="#diagnostico">
                Iniciar diagnóstico
              </a>

              <a className="secondary-link" href="#historial">
                Ver historial
              </a>
            </div>
          </div>

          <div className="status-board">
            <div className="status-card">
              <Activity size={24} />
              <span>Proceso</span>
              <strong>Diagnóstico guiado</strong>
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
              <strong>Historial de casos</strong>
            </div>
          </div>
        </section>

        <section className="feature-grid" aria-label="Resumen del sistema">
          <article className="feature-card">
            <ShieldCheck size={32} />
            <div>
              <h3>Evaluación ordenada</h3>
              <p>Los síntomas se organizan por áreas para facilitar una revisión más precisa.</p>
            </div>
          </article>

          <article className="feature-card">
            <Activity size={32} />
            <div>
              <h3>Diagnóstico preliminar</h3>
              <p>El sistema identifica la falla más probable según los síntomas seleccionados.</p>
            </div>
          </article>

          <article className="feature-card">
            <History size={32} />
            <div>
              <h3>Seguimiento de casos</h3>
              <p>Cada consulta queda registrada para revisar diagnósticos anteriores.</p>
            </div>
          </article>
        </section>

        {error && (
          <div className="notice error">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}

        <section id="diagnostico" className="diagnostic-layout">
          <div className="panel main-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Módulo de análisis</p>
                <h2>Seleccione los síntomas del equipo</h2>
              </div>

              <button className="ghost-button" onClick={limpiarSeleccion}>
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
                      <div className="group-icon">
                        <GroupIcon size={22} />
                      </div>

                      <div>
                        <h3>{grupo.grupo}</h3>
                        <p>{grupo.descripcion}</p>
                      </div>
                    </div>

                    <div className="symptom-list">
                      {grupo.sintomas.map((sintoma) => {
                        const selected = sintomasSeleccionados.includes(sintoma.id);
                        const SymptomIcon = ICONOS_SINTOMA[sintoma.id] || Wrench;

                        return (
                          <button
                            type="button"
                            key={sintoma.id}
                            className={selected ? "symptom selected" : "symptom"}
                            onClick={() => manejarSeleccionSintoma(sintoma.id)}
                          >
                            <SymptomIcon size={18} />

                            <span>{sintoma.nombre}</span>

                            {selected && <CheckCircle2 size={18} className="check" />}
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

            <h2>{sintomasSeleccionados.length} síntomas seleccionados</h2>

            <p className="muted">
              Revise la selección antes de solicitar el diagnóstico. Para mejores
              resultados, seleccione solo síntomas observables.
            </p>

            <div className="selected-list">
              {sintomasSeleccionados.length === 0 ? (
                <span className="empty-state">No hay síntomas seleccionados.</span>
              ) : (
                sintomasSeleccionados.map((id) => (
                  <span className="selected-chip" key={id}>
                    {nombreSintoma(id)}
                  </span>
                ))
              )}
            </div>

            <button
              className="diagnose-button"
              onClick={manejarDiagnostico}
              disabled={cargando || sintomasSeleccionados.length === 0}
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
          <section id="resultado" className="panel result-panel">
            <div className="result-header">
              <div>
                <p className="eyebrow">Resultado generado</p>
                <h2>{resultado.falla_texto}</h2>
              </div>

              <div className={`confidence ${confianza.clase}`}>
                <span>Confianza</span>
                <strong>{confianza.texto}</strong>
              </div>
            </div>

            <div className="result-grid">
              <div className="metric-card">
                <span>Coincidencias</span>
                <strong>{resultado.coincidencias}</strong>
                <small>{confianza.descripcion}</small>
              </div>

              <div className="metric-card">
                <span>Telegram</span>
                <strong>{resultado.telegram_enviado ? "Enviado" : "No enviado"}</strong>
                <small>
                  {resultado.telegram_enviado
                    ? "Notificación entregada correctamente."
                    : "Revise token o chat ID del bot."}
                </small>
              </div>

              <div className="metric-card">
                <span>Síntomas evaluados</span>
                <strong>{resultado.sintomas.length}</strong>
                <small>Entradas usadas por el motor experto.</small>
              </div>
            </div>

            <div className="recommendation">
              <div className="recommendation-icon">
                <Wrench size={24} />
              </div>

              <div>
                <h3>Recomendación técnica</h3>
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

        <section id="historial" className="panel history-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Registro del sistema</p>
              <h2>Historial de diagnósticos</h2>
            </div>

            <button className="ghost-button danger" onClick={manejarLimpiarHistorial}>
              <Trash2 size={17} />
              Limpiar historial
            </button>
          </div>

          {historial.length === 0 ? (
            <div className="history-empty">
              <History size={34} />
              <h3>Sin diagnósticos registrados</h3>
              <p>Cuando realice una consulta, el resultado aparecerá en esta sección.</p>
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
                    <span>{item.telegram_enviado ? "Telegram enviado" : "Telegram pendiente"}</span>
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
      </main>
    </div>
  );
}

export default App;