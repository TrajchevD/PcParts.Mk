import { useEffect, useState } from "react";
import { fetchMotherboards } from "../../api/mbProducts";
import MbCard from "./MbCard";
import MbDetailsModal from "./MbDetailsModal";

export default function MbPicker({ onSelect }) {
  const [mbs, setMbs] = useState([]);
  const [selectedMb, setSelectedMb] = useState(null);
  const [error, setError] = useState(null);

  const [filters, setFilters] = useState({
    socket: "",
    memory_type: "",
    form_factor: "",
    min_price: "",
    max_price: "",
  });
  const [sort, setSort] = useState("price_asc");

  useEffect(() => {
    fetchMotherboards({ ...filters, sort }).then(setMbs);
  }, [filters, sort]);

  return (
    <div className="cpu-page">
      {/* LEFT FILTERS */}
      <aside className="cpu-filters">
        {error && (
          <div className="compat-error">
            ⚠️ {error}
          </div>
        )}
        <h3
          style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
          onClick={() =>
            setSort(s => (s === "price_asc" ? "price_desc" : "price_asc"))
          }
        >
          Motherboards <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Socket
          <select onChange={e => setFilters(f => ({ ...f, socket: e.target.value }))}>
            <option value="">All</option>
            <option value="AM4">AM4</option>
            <option value="AM5">AM5</option>
            <option value="LGA1700">LGA1700</option>
            <option value="LGA1851">LGA1851</option>
          </select>
        </label>

        <label>
          Memory
          <select onChange={e => setFilters(f => ({ ...f, memory_type: e.target.value }))}>
            <option value="">All</option>
            <option value="DDR4">DDR4</option>
            <option value="DDR5">DDR5</option>
          </select>
        </label>

        <label>
          Form factor
          <select onChange={e => setFilters(f => ({ ...f, form_factor: e.target.value }))}>
            <option value="">All</option>
            <option value="mini-ITX">mini-ITX</option>
            <option value="mATX">mATX</option>
            <option value="ATX">ATX</option>
            <option value="E-ATX">E-ATX</option>
          </select>
        </label>
      </aside>

      {/* GRID */}
      <main className="cpu-grid">
        {mbs.map(mb => (
          <MbCard
            key={mb.product_id}
            mb={mb}
            onAdd={async () => {
              try {
                setError(null);
                await onSelect(mb.product_id);
              } catch (err) {
                setError(err.message);
              }
            }}
            onDetails={() => setSelectedMb(mb.product_id)}
          />

        ))}
      </main>

      <MbDetailsModal
        productId={selectedMb}
        onClose={() => setSelectedMb(null)}
        onAdd={async (id) => {
          try {
            setError(null);
            await onSelect(id);
            setSelectedMb(null);
          } catch (err) {
            setError(err.message);
          }
        }}
      />
      
    </div>
  );
}
