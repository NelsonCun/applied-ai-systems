import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import ProvidersPage from "./pages/ProvidersPage";


function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout />
    </ProtectedRoute>
  );
}


export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        element={<ProtectedLayout />}
      >
        <Route
          index
          element={<DashboardPage />}
        />

        <Route
          path="/providers"
          element={<ProvidersPage />}
        />

        <Route
          path="/invoices"
          element={
            <PlaceholderPage
              title="Facturas"
              description={
                "Carga, procesamiento y " +
                "revisión de documentos."
              }
            />
          }
        />

        <Route
          path="/reports"
          element={
            <PlaceholderPage
              title="Reportes"
              description={
                "Generación y descarga de " +
                "reportes administrativos."
              }
            />
          }
        />

        <Route
          path="/automations"
          element={
            <PlaceholderPage
              title="Automatizaciones"
              description={
                "Ejecuciones RPA y evidencia " +
                "del sistema externo."
              }
            />
          }
        />

        <Route
          path="/emails"
          element={
            <PlaceholderPage
              title="Correos"
              description={
                "Historial de entrega de " +
                "reportes por correo."
              }
            />
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />
    </Routes>
  );
}
