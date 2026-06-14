import { useEffect, useState } from "react";

import { apiRequest } from "./api/client";
import Layout from "./components/Layout";
import CategoriesPage from "./pages/CategoriesPage";
import DashboardPage from "./pages/DashboardPage";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import QuestionsPage from "./pages/QuestionsPage";
import SettingsPage from "./pages/SettingsPage";


const TOKEN_KEY = "smartbot_admin_token";


function App() {
  const [token, setToken] = useState(
    () =>
      window.localStorage.getItem(
        TOKEN_KEY
      ) ?? ""
  );

  const [currentUser, setCurrentUser] =
    useState(null);

  const [checkingSession, setCheckingSession] =
    useState(Boolean(token));

  const [activeView, setActiveView] =
    useState("dashboard");

  const [toast, setToast] =
    useState(null);

  const notify = (
    message,
    type = "success"
  ) => {
    setToast({
      message,
      type,
    });

    window.setTimeout(() => {
      setToast(null);
    }, 4200);
  };

  const logout = () => {
    window.localStorage.removeItem(
      TOKEN_KEY
    );

    setToken("");
    setCurrentUser(null);
    setActiveView("dashboard");
  };

  useEffect(() => {
    if (!token) {
      setCheckingSession(false);
      return;
    }

    let mounted = true;

    const verifySession = async () => {
      setCheckingSession(true);

      try {
        const user = await apiRequest(
          "/auth/me",
          { token }
        );

        if (mounted) {
          setCurrentUser(user);
        }
      } catch {
        if (mounted) {
          logout();
        }
      } finally {
        if (mounted) {
          setCheckingSession(false);
        }
      }
    };

    verifySession();

    return () => {
      mounted = false;
    };
  }, [token]);

  const handleLogin = (data) => {
    window.localStorage.setItem(
      TOKEN_KEY,
      data.access_token
    );

    setToken(data.access_token);
    setCurrentUser(data.user);

    notify(
      `Bienvenido, ${data.user.full_name}.`
    );
  };

  if (checkingSession) {
    return (
      <main className="session-loading">
        <div className="brand-symbol brand-symbol-large">
          SB
        </div>

        <span className="spinner" />

        <p>Validando sesión...</p>
      </main>
    );
  }

  if (!token) {
    return (
      <LoginPage onLogin={handleLogin} />
    );
  }

  const renderPage = () => {
    switch (activeView) {
      case "categories":
        return (
          <CategoriesPage
            token={token}
            notify={notify}
          />
        );

      case "questions":
        return (
          <QuestionsPage
            token={token}
            notify={notify}
          />
        );

      case "history":
        return (
          <HistoryPage token={token} />
        );

      case "settings":
        return (
          <SettingsPage
            token={token}
            notify={notify}
          />
        );

      case "dashboard":
      default:
        return (
          <DashboardPage token={token} />
        );
    }
  };

  return (
    <>
      <Layout
        activeView={activeView}
        onChangeView={setActiveView}
        currentUser={currentUser}
        onLogout={logout}
      >
        {renderPage()}
      </Layout>

      {toast && (
        <div
          className={`toast toast-${toast.type}`}
          role="status"
        >
          {toast.message}
        </div>
      )}
    </>
  );
}


export default App;
