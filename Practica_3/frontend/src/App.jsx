import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import DashboardPage from "./pages/DashboardPage";
import InvoicesPage from "./pages/InvoicesPage";
import LoginPage from "./pages/LoginPage";
import ProvidersPage from "./pages/ProvidersPage";
import ReportsPage from "./pages/ReportsPage";
import AutomationsPage from "./pages/AutomationsPage";
import EmailsPage from "./pages/EmailsPage";


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
          element={<InvoicesPage />}
        />
        <Route
          path="/reports"
          element={<ReportsPage />}
        />
        <Route
          path="/automations"
          element={<AutomationsPage />}
        />


        <Route
          path="/emails"
          element={<EmailsPage />}
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
