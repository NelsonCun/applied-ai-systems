import { useState } from "react";


const NAVIGATION = [
  {
    id: "dashboard",
    label: "Resumen",
    symbol: "IN",
  },
  {
    id: "categories",
    label: "Categorías",
    symbol: "CA",
  },
  {
    id: "questions",
    label: "Preguntas y respuestas",
    symbol: "PR",
  },
  {
    id: "history",
    label: "Historial",
    symbol: "HI",
  },
  {
    id: "settings",
    label: "Configuración",
    symbol: "CO",
  },
];


function Layout({
  activeView,
  onChangeView,
  currentUser,
  onLogout,
  children,
}) {
  const [mobileOpen, setMobileOpen] =
    useState(false);

  const currentItem =
    NAVIGATION.find(
      (item) => item.id === activeView
    ) ?? NAVIGATION[0];

  const changeView = (view) => {
    onChangeView(view);
    setMobileOpen(false);
  };

  return (
    <div className="app-shell">
      <aside
        className={
          mobileOpen
            ? "sidebar sidebar-open"
            : "sidebar"
        }
      >
        <div className="sidebar-brand">
          <div className="brand-symbol">
            SB
          </div>

          <div>
            <strong>SmartBot</strong>
            <span>Hospital Vida Central</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAVIGATION.map((item) => (
            <button
              key={item.id}
              type="button"
              className={
                activeView === item.id
                  ? "nav-button nav-button-active"
                  : "nav-button"
              }
              onClick={() =>
                changeView(item.id)
              }
            >
              <span className="nav-symbol">
                {item.symbol}
              </span>

              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-summary">
            <div className="user-avatar">
              {currentUser?.full_name
                ?.charAt(0)
                ?.toUpperCase() ?? "A"}
            </div>

            <div>
              <strong>
                {currentUser?.full_name ??
                  "Administrador"}
              </strong>

              <span>
                {currentUser?.username}
              </span>
            </div>
          </div>

          <button
            type="button"
            className="btn btn-secondary btn-full"
            onClick={onLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {mobileOpen && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Cerrar menú"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <main className="content-area">
        <header className="topbar">
          <button
            type="button"
            className="mobile-menu-button"
            onClick={() =>
              setMobileOpen((value) => !value)
            }
            aria-label="Abrir menú"
          >
            ☰
          </button>

          <div>
            <p className="eyebrow">
              Panel administrativo
            </p>

            <h1>{currentItem.label}</h1>
          </div>

          <div className="topbar-status">
            <span className="status-dot" />
            Sistema disponible
          </div>
        </header>

        <div className="content-scroll">
          {children}
        </div>
      </main>
    </div>
  );
}


export default Layout;
