import { useAuth } from "../auth/AuthContext";

export default function Tabs({ active, setActive }) {
  const { token } = useAuth();

  function open(tab) {
    setActive(tab);
  }

  return (
    <div className="tabs">
      <button onClick={() => open("products")}>
        Products
      </button>

      <button onClick={() => open("alerts")}>
        Alerts { !token && "🔒" }
      </button>

      <button onClick={() => open("notifications")}>
        Notifications { !token && "🔒" }
      </button>
    </div>
  );
}
