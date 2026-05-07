import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { useToast } from "../components/Toast";
import { apiFetch } from "../api/api";

export default function AlertsPanel() {
  const { token } = useAuth();
  const toast = useToast();
  const [alertName, setAlertName] = useState("");
  const [category, setCategory] = useState("cpu");
  const [titleQuery, setTitleQuery] = useState("");
  const [storeName, setStoreName] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [loading, setLoading] = useState(false);

  if (!token) {
    return (
      <div style={{ color: "var(--text-dim)", padding: 8 }}>
        Please log in to create price alerts.
      </div>
    );
  }

  async function submitAlert() {
    if (!alertName.trim() || !maxPrice) {
      toast.error("Alert name and max price are required.");
      return;
    }

    setLoading(true);
    try {
      await apiFetch("/api/alerts", {
        method: "POST",
        body: JSON.stringify({
          alert_name: alertName,
          category_slug: category,
          title_query: titleQuery,
          store_name: storeName || null,
          max_price: Number(maxPrice),
        }),
      });
      toast.success("Price alert created!");
      setAlertName("");
      setTitleQuery("");
      setStoreName("");
      setMaxPrice("");
    } catch (e) {
      toast.error(e.message || "Failed to create alert.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="alerts-panel">
      <h3>Price Alert</h3>

      <label>
        Alert name
        <input value={alertName} onChange={e => setAlertName(e.target.value)} placeholder="e.g. Ryzen CPU deal" />
      </label>

      <label>
        Category
        <select value={category} onChange={e => setCategory(e.target.value)}>
          <option value="cpu">CPU</option>
          <option value="gpu">GPU</option>
          <option value="ram">RAM</option>
          <option value="mb">Motherboard</option>
          <option value="storage">Storage</option>
        </select>
      </label>

      <label>
        Product keyword
        <input value={titleQuery} onChange={e => setTitleQuery(e.target.value)} placeholder="ryzen 7700, rtx 4060…" />
      </label>

      <label>
        Store (optional)
        <input value={storeName} onChange={e => setStoreName(e.target.value)} placeholder="Anhoch, Setec…" />
      </label>

      <label>
        Max price (MKD)
        <input type="number" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} placeholder="e.g. 30000" min="1" />
      </label>

      <button className="btn-primary" onClick={submitAlert} disabled={loading} style={{ width: "100%" }}>
        {loading
          ? <><span className="loading-spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Saving…</>
          : "Save Alert"
        }
      </button>
    </div>
  );
}
