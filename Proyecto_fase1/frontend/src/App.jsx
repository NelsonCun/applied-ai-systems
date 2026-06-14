import { useEffect, useState } from "react";
import {
  Cpu,
  History,
  Settings,
  Stethoscope,
} from "lucide-react";

import DiagnosticoView from "./views/DiagnosticoView";
import HistorialView from "./views/HistorialView";
import AdminView from "./views/AdminView";
import {
  eliminarHistorial,
  obtenerHistorial,
  obtenerSintomas,
} from "./services/api";
import "./App.css";

const VISTAS = {
  diagnostico: {
    etiqueta: "Diagnóstico",
    icono: Stethoscope,
  },
  historial: {
    etiqueta: "Historial",
    icono: History,
  },
  administracion: {
    etiqueta: "Administración",
    icono: Settings,
  },
};

function App() {
  const [vistaActiva, setVistaActiva] = useState("diagnostico");
  const [sintomas, setSintomas] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [errorGlobal, setErrorGlobal] = useState("");
  const [cargandoInicial, setCargandoInicial] = useState(true);

  useEffect(() => {
    let componenteActivo = true;

    async function cargarDatosIniciales() {
      try {
        const [sintomasData, historialData] = await Promise.all([
          obtenerSintomas(),
          obtenerHistorial(),
        ]);

        if (!componenteActivo) return;

        setSintomas(sintomasData);
        setHistorial([...historialData].reverse());
      } catch (error) {
        console.error("No se pudo cargar la aplicación:", error);

        if (componenteActivo) {
          setErrorGlobal(
            "No se pudo cargar la información. Verifique que el servidor esté activo.",
          );
        }
      } finally {
        if (componenteActivo) {
          setCargandoInicial(false);
        }
      }
    }

    cargarDatosIniciales();

    return () => {
      componenteActivo = false;
    };
  }, []);

  async function recargarSintomas() {
    const data = await obtenerSintomas();
    setSintomas(data);
  }

  async function recargarHistorial() {
    const data = await obtenerHistorial();
    setHistorial([...data].reverse());
  }

  async function limpiarHistorial() {
    await eliminarHistorial();
    setHistorial([]);
  }

  function cambiarVista(vista) {
    setVistaActiva(vista);
    setErrorGlobal("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="shell">
      <header className="topbar">
        <button
          type="button"
          className="brand"
          onClick={() => cambiarVista("diagnostico")}
          aria-label="Ir al diagnóstico"
        >
          <span className="brand-mark">
            <Cpu size={26} />
          </span>

          <span>
            <span className="brand-title">Doctor Byte</span>
            <span className="brand-subtitle">Centro de diagnóstico</span>
          </span>
        </button>

        <nav className="nav" aria-label="Navegación principal">
          {Object.entries(VISTAS).map(([clave, item]) => {
            const Icono = item.icono;

            return (
              <button
                type="button"
                key={clave}
                className={
                  vistaActiva === clave ? "nav-button active" : "nav-button"
                }
                onClick={() => cambiarVista(clave)}
              >
                <Icono size={17} />
                {item.etiqueta}
              </button>
            );
          })}
        </nav>
      </header>

      {errorGlobal && (
        <div className="global-notice" role="alert">
          {errorGlobal}
        </div>
      )}

      <main className="layout">
        {cargandoInicial ? (
          <section className="panel loading-panel">
            <div className="loading-ring" />
            <p>Cargando Doctor Byte...</p>
          </section>
        ) : (
          <>
            {vistaActiva === "diagnostico" && (
              <DiagnosticoView
                sintomas={sintomas}
                onHistorialActualizado={recargarHistorial}
              />
            )}

            {vistaActiva === "historial" && (
              <HistorialView
                historial={historial}
                sintomas={sintomas}
                onRecargar={recargarHistorial}
                onLimpiar={limpiarHistorial}
              />
            )}

            {vistaActiva === "administracion" && (
              <AdminView onConocimientoActualizado={recargarSintomas} />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
