import { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ProductFlyout from "./ProductFlyout";
import { createBuild } from "../api/buildManager";
import { useAuth } from "../auth/AuthContext";
import { apiFetch } from "../api/api";

export default function Sidebar({ isOpen, onClose, onShowLogin, onShowAlerts, onShowNotifications }) {
  const location = useLocation();
  const navigate = useNavigate();
  const wrapperRef = useRef(null);
  const { token, logout } = useAuth();

  const isActive = (path) => location.pathname === path;
  const [showFlyout, setShowFlyout] = useState(false);
  const [creatingBuild, setCreatingBuild] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!token) { setUnreadCount(0); return; }
    apiFetch("/api/notifications")
      .then(data => setUnreadCount(data.filter(n => !n.is_read).length))
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    if (!showFlyout) return;
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowFlyout(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showFlyout]);

  useEffect(() => {
    function handleEsc(e) { if (e.key === "Escape") { setShowFlyout(false); onClose(); } }
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  async function handleNewBuild() {
    if (creatingBuild) return;
    setCreatingBuild(true);
    try {
      const data = await createBuild("New Build");
      onClose();
      navigate(`/builder-v2/${data.build_id}`);
    } catch {
      // silently fail — user sees no build created
    } finally {
      setCreatingBuild(false);
    }
  }

  function handleNavClick() {
    setShowFlyout(false);
    onClose();
  }

  function handleAlertsClick() {
    onClose();
    onShowAlerts();
  }

  function handleNotificationsClick() {
    onClose();
    onShowNotifications();
  }

  return (
    <aside className={`sidebar${isOpen ? " open" : ""}`}>
      {/* Mobile close button */}
      <button className="sidebar-close-btn" onClick={onClose} aria-label="Close menu">✕</button>

      {/* Brand */}
      <div className="sidebar-header">
        <Link to="/" className="brand" onClick={handleNavClick}>
          <span className="logo-icon">⚡</span>
          <div className="logo-text">
            <span style={{ fontSize: "1.05rem", fontWeight: 800 }}>PcBuilderMk</span>
            <span className="version-badge">BETA v0.3.6</span>
          </div>
        </Link>

        {/* Auth */}
        <div className="user-menu">
          {token ? (
            <>
              <div className="user-actions">
                <button className="btn-text" style={{ padding: "5px 8px", fontSize: "0.8rem" }} onClick={handleAlertsClick}>
                  🔎 Price Alerts
                </button>
                <button
                  className="btn-text"
                  style={{ padding: "5px 8px", fontSize: "0.8rem", position: "relative" }}
                  onClick={handleNotificationsClick}
                >
                  🔔 Notifications
                  {unreadCount > 0 && (
                    <span style={{
                      position: "absolute", top: 0, right: 0,
                      background: "#ef4444", color: "white",
                      fontSize: "9px", fontWeight: 700,
                      padding: "1px 5px", borderRadius: "999px",
                      lineHeight: 1.4
                    }}>
                      {unreadCount}
                    </span>
                  )}
                </button>
              </div>
              <button className="btn-text" style={{ padding: "5px 8px", fontSize: "0.8rem" }} onClick={logout}>
                Log Out
              </button>
            </>
          ) : (
            <div className="auth-buttons">
              <button className="btn-text" onClick={() => { onClose(); onShowLogin(); }}>Log In</button>
              <button className="btn-primary small" onClick={() => { onClose(); onShowLogin(); }}>Sign Up</button>
            </div>
          )}
        </div>

        {/* Social */}
        <div className="social-buttons">
          <a href="#" className="social-btn discord">🎮 Discord</a>
          <a href="#" className="social-btn reddit">🔴 Reddit</a>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {/* PC Builder */}
        <div className="nav-item-group">
          <Link to="/builds" className={`nav-item ${isActive("/builds") ? "active" : ""}`} style={{ flex: 1 }} onClick={handleNavClick}>
            🛠️ PC Builder
          </Link>
          <button
            className="badge-new"
            onClick={handleNewBuild}
            disabled={creatingBuild}
            title="Create new build"
          >
            {creatingBuild ? "…" : "+ New"}
          </button>
        </div>

        {/* Products flyout */}
        <div className="nav-item-wrapper" ref={wrapperRef}>
          <button
            className={`nav-item ${location.pathname.startsWith("/catalog") ? "active" : ""}`}
            onClick={() => setShowFlyout(prev => !prev)}
          >
            📦 Products
            <span className={`nav-chevron ${showFlyout ? "open" : ""}`}>▾</span>
          </button>
          <ProductFlyout visible={showFlyout} onClose={() => { setShowFlyout(false); onClose(); }} />
        </div>

        {/* My Builds */}
        <Link to="/builds" className={`nav-item ${isActive("/builds") ? "active" : ""}`} onClick={handleNavClick}>
          🖥️ My Builds
          <span className="nav-badge badge-blue">Saves</span>
        </Link>

        <div className="nav-group-label">Tools</div>

        <Link to="/compare" className={`nav-item ${isActive("/compare") ? "active" : ""}`} onClick={handleNavClick}>
          ⚖️ Compare Parts
        </Link>

        <Link to="/recommend" className={`nav-item ${isActive("/recommend") ? "active" : ""}`} onClick={handleNavClick}>
          🤖 AI Recommend
        </Link>
      </nav>
    </aside>
  );
}
