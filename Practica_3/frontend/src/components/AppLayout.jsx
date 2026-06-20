import {
  BarChart3,
  Bot,
  Building2,
  FileSpreadsheet,
  LogOut,
  Mail,
  Menu,
  PanelLeftClose,
  ReceiptText,
  ScanText,
} from "lucide-react";

import {
  NavLink,
  Outlet,
} from "react-router-dom";

import { useState } from "react";

import { useAuth } from "../context/AuthContext";


const navigation = [
  {
    path: "/",
    label: "Dashboard",
    icon: BarChart3,
    end: true,
  },
  {
    path: "/providers",
    label: "Proveedores",
    icon: Building2,
  },
  {
    path: "/invoices",
    label: "Facturas",
    icon: ReceiptText,
  },
  {
    path: "/reports",
    label: "Reportes",
    icon: FileSpreadsheet,
  },
  {
    path: "/automations",
    label: "Automatizaciones",
    icon: Bot,
  },
  {
    path: "/emails",
    label: "Correos",
    icon: Mail,
  },
];


export default function AppLayout() {
  const { user, logout } = useAuth();

  const [
    sidebarCollapsed,
    setSidebarCollapsed,
  ] = useState(false);

  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);


  function handleLogout() {
    logout();
    window.location.replace("/login");
  }


  return (
    <div
      className={[
        "app-shell",
        sidebarCollapsed
          ? "app-shell-collapsed"
          : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <aside
        className={[
          "sidebar",
          mobileOpen
            ? "sidebar-mobile-open"
            : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <div className="sidebar-brand">
          <div className="sidebar-brand-mark">
            <ScanText size={24} />
          </div>

          <div className="sidebar-brand-copy">
            <strong>SmartInvoice</strong>
            <span>Gestión documental</span>
          </div>
        </div>

        <div className="sidebar-section-label">
          Navegación
        </div>

        <nav className="sidebar-navigation">
          {navigation.map(
            ({
              path,
              label,
              icon: Icon,
              end,
            }) => (
              <NavLink
                key={path}
                to={path}
                end={end}
                onClick={() =>
                  setMobileOpen(false)
                }
                className={({
                  isActive,
                }) =>
                  [
                    "navigation-link",
                    isActive
                      ? "navigation-link-active"
                      : "",
                  ]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                <span className="navigation-icon">
                  <Icon size={19} />
                </span>

                <span className="navigation-label">
                  {label}
                </span>
              </NavLink>
            ),
          )}
        </nav>

        <div className="sidebar-footer">

          <button
            className="sidebar-logout"
            type="button"
            onClick={handleLogout}
          >
            <LogOut size={18} />

            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      {mobileOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label="Cerrar menú"
          onClick={() =>
            setMobileOpen(false)
          }
        />
      )}

      <section className="application-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="topbar-icon-button mobile-menu-button"
              type="button"
              aria-label="Abrir menú"
              onClick={() =>
                setMobileOpen(true)
              }
            >
              <Menu size={20} />
            </button>

            <button
              className="topbar-icon-button collapse-button"
              type="button"
              aria-label="Contraer menú"
              onClick={() =>
                setSidebarCollapsed(
                  (current) => !current,
                )
              }
            >
              <PanelLeftClose size={20} />
            </button>

            <div className="topbar-context">
              <span>Panel administrativo</span>
              <strong>SmartInvoice</strong>
            </div>
          </div>

          <div className="topbar-user">
            <div className="topbar-user-avatar">
              {user?.full_name
                ?.charAt(0)
                ?.toUpperCase() || "A"}
            </div>

            <div className="topbar-user-copy">
              <strong>
                {user?.full_name}
              </strong>

              <span>
                {user?.role === "ADMIN"
                  ? "Administrador"
                  : user?.role}
              </span>
            </div>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </section>
    </div>
  );
}
