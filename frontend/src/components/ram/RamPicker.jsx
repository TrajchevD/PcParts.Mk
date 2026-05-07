import { useEffect, useState } from "react";
import { fetchRams } from "../../api/ramProducts";
import RamCard from "./RamCard";
import RamDetailsModal from "./RamDetailsModal";

export default function RamPicker({ onSelect }) {
  const [rams, setRams] = useState([]);
  const [selected, setSelected] = useState(null);
   const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    memory_type: "",
    capacity_gb: "",
  });

  useEffect(() => {
    fetchRams(filters).then(setRams);
  }, [filters]);

  return (
    <div className="cpu-page">
      <aside className="cpu-filters">
        {error && (
  <div className="compat-error">
    ⚠️ {error}
  </div>
)}

        <h3>RAM</h3>

        <label>
          Memory
          <select onChange={e => setFilters(f => ({ ...f, memory_type: e.target.value }))}>
            <option value="">All</option>
            <option value="DDR4">DDR4</option>
            <option value="DDR5">DDR5</option>
          </select>
        </label>

        <label>
          Min Capacity (GB)
          <select onChange={e => setFilters(f => ({ ...f, capacity_gb: e.target.value }))}>
            <option value="">Any</option>
            <option value="16">16+</option>
            <option value="32">32+</option>
            <option value="64">64+</option>
          </select>
        </label>
      </aside>

      <main className="cpu-grid">
        {rams.map(r => (
          <RamCard
            key={r.product_id}
            ram={r}
            onDetails={setSelected}
            onAdd={async () => {
              try {
                setError(null);
                await onSelect(r.product_id);
              } catch (err) {
                setError(err.message);
              }
            }}
          />

        ))}
      </main>

      <RamDetailsModal
        productId={selected}
        onClose={() => setSelected(null)}
        onAdd={async (id) => {
          try {
            setError(null);
            await onSelect(id);
            setSelected(null);
          } catch (err) {
            setError(err.message);
          }
        }}
      />

    </div>
  );
}
