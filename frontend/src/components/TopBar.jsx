import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function TopBar({ onShowLogin, onToggleSidebar }) {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/catalog/gpu?q=${encodeURIComponent(query.trim())}`);
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
