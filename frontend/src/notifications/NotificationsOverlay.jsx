// components/NotificationsOverlay.jsx

import NotificationsPanel from "../notifications/NotificationsPanel";

export default function NotificationsOverlay({ onClose }) {
  return (
    <div className="notifications-backdrop" onClick={onClose}>
      <div
        className="notifications-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="notifications-close" onClick={onClose}>
          ✕
        </button>

        <NotificationsPanel />
      </div>
    </div>
  );
}