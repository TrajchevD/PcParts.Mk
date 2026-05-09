import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const CATALOG_PAGES = [
  "/catalog/cpu",
  "/catalog/gpu",
  "/catalog/mb",
  "/catalog/ram",
  "/catalog/storage",
];

export default function TopBar({ onShowLogin, onToggleSidebar }) {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [query, setQuery] = useState("");

  function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    const q = encodeURIComponent(query.trim());
    const target = CATALOG_PAGES.find(p => location.pathname.startsWith(p)) || "/catalog/gpu";
    navigate(`${target}?q=${q}`);
    setQuery("");
  }

  return (
    <header className="topbar">
      {/* Hamburger — visible only on mobile via CSS */}
      <button
        className="hamburger-btn"
        onClick={onToggleSidebar}
        aria-label="Toggle navigation menu"
      >
        ☰
      </button>

      <form className="search-bar" onSubmit={handleSearch}>
        <span className="search-icon">🔍</span>
        <input
          type="text"
          placeholder="Search parts…"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <span className="search-shortcut">⌘K</span>
      </form>

      {/* Auth actions — hidden on mobile (accessible via sidebar) */}
      <div className="topbar-actions">
        {token ? (
          <button className="btn-text" onClick={logout}>Log Out</button>
        ) : (
          <div className="auth-buttons">
            <button className="btn-text" onClick={onShowLogin}>Log In</button>
            <button className="btn-primary small" onClick={onShowLogin}>Sign Up</button>
          </div>
        )}
      </div>
    </header>
  );
}
