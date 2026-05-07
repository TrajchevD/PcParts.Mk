import { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import AlertsPanel from "../alerts/AlertsPanel";
import NotificationsOverlay from "../notifications/NotificationsOverlay";
import AuthForm from "../auth/AuthForm";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import { createBuild } from "../api/buildManager";

const TABS = [
  { id: "browse",  label: "Browse",  icon: "⊞", path: "/" },
  { id: "compare", label: "Compare", icon: "⊟", path: "/compare" },
  { id: "builder", label: "Builder", icon: "⚙", path: null },
  { id: "recs",    label: "Recs",    icon: "✦", path: "/recommend" },
  { id: "alerts",  label: "Alerts",  icon: "🔔", path: null },
];

export default function Layout() {
  const [showAlerts, setShowAlerts] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { token } = useAuth();
  const navigate = useNavigate();

  function closeSidebar() { setSidebarOpen(false); }
  function toggleSidebar() { setSidebarOpen(prev => !prev); }

  async function handleBuilderTab() {
    try {
      const data = await createBuild("My Build");
      navigate(`/builder-v2/${data.build_id}`);
    } catch {
      navigate("/builds");
    }
  }

  return (
    <div className="app-layout">
      {/* Mobile sidebar backdrop — click to close */}
      <div
        className={`sidebar-backdrop${sidebarOpen ? " visible" : ""}`}
        onClick={closeSidebar}
      />

      <Sidebar
        isOpen={sidebarOpen}
        onClose={closeSidebar}
        onShowLogin={() => setShowLogin(true)}
        onShowAlerts={() => setShowAlerts(true)}
        onShowNotifications={() => setShowNotifications(true)}
      />

      <div className="main-area">
        <TopBar
          onShowLogin={() => setShowLogin(true)}
          onToggleSidebar={toggleSidebar}
        />
        <main className="page-content">
          <Outlet context={{ toggleSidebar }} />
        </main>
      </div>

      {/* ── Mobile bottom tab bar ── */}
      <nav className="mob-tab-bar mob-only">
        {TABS.map(tab => {
          if (tab.id === "alerts") {
            return (
              <button
                key={tab.id}
                className="mob-tab"
                onClick={() => setShowAlerts(true)}
              >
                <span className="mob-tab-icon">{tab.icon}</span>
                <span className="mob-tab-label">{tab.label}</span>
              </button>
            );
          }
          if (tab.id === "builder") {
            return (
              <button
                key={tab.id}
                className="mob-tab"
                onClick={handleBuilderTab}
              >
                <span className="mob-tab-icon">{tab.icon}</span>
                <span className="mob-tab-label">{tab.label}</span>
              </button>
            );
          }
          return (
            <NavLink
              key={tab.id}
              to={tab.path}
              end={tab.path === "/"}
              className={({ isActive }) =>
                `mob-tab${isActive ? " mob-tab-active" : ""}`
              }
            >
              {({ isActive }) => (
                <>
                  <span className="mob-tab-icon">{tab.icon}</span>
                  {isActive && <span className="mob-tab-dot" />}
                  <span className="mob-tab-label">{tab.label}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Alerts panel (compact overlay) */}
      {showAlerts && (
        <div className="overlayBackdrop" onClick={() => setShowAlerts(false)}>
          <div className="overlayPanel" onClick={e => e.stopPropagation()}>
            <button className="closeBtn" onClick={() => setShowAlerts(false)}>✕</button>
            {token
              ? <AlertsPanel />
              : <p style={{ color: "var(--text-dim)", margin: 0 }}>Please log in to manage price alerts.</p>
            }
          </div>
        </div>
      )}

      {/* Notifications (full-width overlay) */}
      {showNotifications && (
        <NotificationsOverlay onClose={() => setShowNotifications(false)} />
      )}

      {/* Login / Register modal */}
      {showLogin && (
        <div className="overlayBackdrop" onClick={() => setShowLogin(false)}>
          <div className="overlayPanel" onClick={e => e.stopPropagation()}>
            <button className="closeBtn" onClick={() => setShowLogin(false)}>✕</button>
            <AuthForm onClose={() => setShowLogin(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
