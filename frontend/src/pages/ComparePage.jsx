import { useState } from "react";
import CompareTable from "../components/compare/CompareTable";
import CompareSlots from "../components/compare/CompareSlots";
import { compareParts } from "../api/compare";

const CATEGORIES = [
  { value: "cpu",     label: "CPU" },
  { value: "gpu",     label: "GPU" },
  { value: "ram",     label: "RAM" },
  { value: "mb",      label: "Motherboard" },
  { value: "storage", label: "Storage" },
];

export default function ComparePage() {
  const [category, setCategory] = useState("cpu");
  const [slots, setSlots] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  async function runCompare(ids) {
    const validIds = ids.filter(Boolean);
    if (validIds.length < 1) { setItems([]); return; }
    setLoading(true);
    try {
      const res = await compareParts(category, validIds);
      setItems(res.items ?? []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  function handleCategoryChange(cat) {
    setCategory(cat);
    setSlots([]);
    setItems([]);
  }

  function handleSlotsChange(ids) {
    setSlots(ids);
    runCompare(ids);
  }

  function handleAdd(id) {
    const next = [...slots, id];
    setSlots(next);
    runCompare(next);
  }

  function handleRemove(id) {
    const next = slots.filter(s => s !== id);
    setSlots(next);
    runCompare(next);
  }

  return (
    <div className="compare-page">
      <h2>Compare PC Parts</h2>
      <p className="muted" style={{ marginBottom: 0 }}>Select a category and add up to 4 parts to compare side-by-side.</p>

      <div className="compare-controls">
        <label style={{ flexDirection: "row", alignItems: "center", gap: 8, color: "var(--text-dim)", fontSize: "0.85rem" }}>
          Category:
          <select
            value={category}
            onChange={e => handleCategoryChange(e.target.value)}
            style={{ width: "auto", marginBottom: 0 }}
          >
            {CATEGORIES.map(c => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </label>

        {loading && (
          <span style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-dim)", fontSize: "0.85rem" }}>
            <span className="loading-spinner" /> Comparing…
          </span>
        )}
      </div>

      <CompareSlots
        category={category}
        slots={slots}
        items={items}
        onChange={handleSlotsChange}
      />

      {items.length > 0 && (
        <div className="compare-table-wrapper">
          <CompareTable
            category={category}
            items={items}
            onAdd={handleAdd}
            onRemove={handleRemove}
          />
        </div>
      )}

      {items.length === 0 && slots.length === 0 && (
        <div className="empty-state" style={{ marginTop: 40 }}>
          <span className="empty-icon">⚖️</span>
          <h3>Nothing to compare yet</h3>
          <p>Click "+ Add product" to pick parts and compare their specs.</p>
        </div>
      )}
    </div>
  );
}
