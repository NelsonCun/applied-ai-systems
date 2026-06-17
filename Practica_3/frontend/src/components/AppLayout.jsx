import {
  BarChart3,
  Bot,
  Building2,
  FileSpreadsheet,
  FileText,
  LogOut,
  Mail,
  Menu,
  PanelLeftClose,
  ReceiptText,
  ShieldCheck,
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
          ? "sidebar-collapsed"
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
        <div className="brand">
          <div className="brand-symbol">
            <FileText size={25} />
          </div>

          <div className="brand-copy">
            <strong>SmartInvoice</strong>
            <span>Administración inteligente</span>
          </div>
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
                onClick={() =>
                  setMobileOpen(false)
                }
              >
                <Icon size={20} />

                <span>{label}</span>
              </NavLink>
            ),
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="security-badge">
            <ShieldCheck size={19} />

            <div>
              <strong>Sesión protegida</strong>
              <span>JWT activo</span>
            </div>
          </div>

          <button
            className="logout-button"
            type="button"
            onClick={handleLogout}
          >
            <LogOut size={19} />
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
          <div className="topbar-actions">
            <button
              className="icon-button mobile-menu-button"
              type="button"
              aria-label="Abrir menú"
              onClick={() =>
                setMobileOpen(true)
              }
            >
              <Menu size={21} />
            </button>

            <button
              className="icon-button collapse-button"
              type="button"
              aria-label="Contraer menú"
              onClick={() =>
                setSidebarCollapsed(
                  (current) => !current,
                )
              }
            >
              <PanelLeftClose size={21} />
            </button>
          </div>

          <div className="topbar-user">
            <div className="user-avatar">
              {user?.full_name
                ?.charAt(0)
                ?.toUpperCase() || "A"}
            </div>

            <div className="user-copy">
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
