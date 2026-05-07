import { useEffect, useState } from "react";
import { apiFetch } from "../api/api";
import { useAuth } from "../auth/AuthContext";
import LoginForm from "../auth/AuthForm";

export default function NotificationsPanel() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);

  useEffect(() => {
    if (!token) return;

    async function load() {
      const data = await apiFetch("/api/notifications");
      setItems(data);

      const unread = data.filter(n => !n.is_read);
      await Promise.all(
        unread.map(n =>
          apiFetch(`/api/notifications/${n.notification_id}/read`, { method: "POST" }).catch(() => {})
        )
      );
    }

    load();
  }, [token]);

  if (!token) {
    return (
      <div className="card">
        <h3>Login required</h3>
        <LoginForm />
      </div>
    );
  }

  return (
    <div className="notification-container">
      <h2>Notifications</h2>

      {items.length === 0 && (
        <p className="muted">No notifications yet.</p>
      )}

      {items.map(n => (
        <div key={n.notification_id} className="notification-block">
          <h4 className="notification-title">{n.title}</h4>
          <p className="notification-message">{n.message}</p>

          <div className="notification-grid">
            {n.payload.map(p => (
              <div key={p.id} className="notification-card">
                <div className="notification-image-wrapper">
                  <img src={p.image} alt={p.title} />
                  <span className="notification-badge">Alert</span>
                </div>

                <div className="notification-body">
                  <div className="notification-product-title">
                    {p.title}
                  </div>

                  <div className="notification-price">
                    {p.price_text}
                  </div>

                  <div className="notification-store">
                    {p.store}
                  </div>

                  <a
                    href={p.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="notification-link"
                  >
                    View Deal →
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}