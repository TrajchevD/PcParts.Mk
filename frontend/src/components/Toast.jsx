/**
 * Lightweight toast notification system.
 *
 * Usage:
 *   import { useToast } from "./Toast";
 *   const toast = useToast();
 *   toast.success("Build saved!");
 *   toast.error("Something went wrong.");
 *   toast.info("Checking prices…");
 */

import { createContext, useCallback, useContext, useState } from "react";

const ToastContext = createContext(null);

let _nextId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const add = useCallback((message, type = "info", duration = 3500) => {
    const id = ++_nextId;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => remove(id), duration);
  }, [remove]);

  const api = {
    success: (msg, ms) => add(msg, "success", ms),
    error:   (msg, ms) => add(msg, "error", ms ?? 5000),
    info:    (msg, ms) => add(msg, "info", ms),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-container" aria-live="polite">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            <span className="toast-icon">
              {t.type === "success" ? "✓" : t.type === "error" ? "✕" : "ℹ"}
            </span>
            <span className="toast-message">{t.message}</span>
            <button className="toast-close" onClick={() => remove(t.id)} aria-label="Dismiss">×</button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside <ToastProvider>");
  return ctx;
}
