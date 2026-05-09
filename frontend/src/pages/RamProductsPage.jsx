import { useEffect, useState } from "react";
import { fetchRams } from "../api/ramProducts";
import RamCard from "../components/ram/RamCard";
import RamDetailsModal from "../components/ram/RamDetailsModal";
import CategoryNav from "../components/CategoryNav";

export default function RamProductsPage() {
  const [rams, setRams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [filters, setFilters] = useState({ memory_type: "", capacity_gb: "", min_price: "", max_price: "" });

  useEffect(() => {
    setLoading(true);
    fetchRams(filters).then(setRams).finally(() => setLoading(false));
  }, [filters]);

  return (
    <div className="cpu-page">
      <CategoryNav />
      <aside className="cpu-filters">
        <h3>RAM</h3>

        <label>
          Memory Type
          <select value={filters.memory_type} onChange={e => setFilters(f => ({ ...f, memory_type: e.target.value }))}>
            <option value="">All</option>
            <option value="DDR4">DDR4</option>
            <option value="DDR5">DDR5</option>
          </select>
        </label>

        <label>
          Min Capacity
          <select value={filters.capacity_gb} onChange={e => setFilters(f => ({ ...f, capacity_gb: e.target.value }))}>
            <option value="">Any</option>
            <option value="8">8 GB+</option>
            <option value="16">16 GB+</option>
            <option value="32">32 GB+</option>
            <option value="64">64 GB+</option>
          </select>
        </label>

        <label>
          Min Price
          <input type="number" value={filters.min_price} onChange={e => setFilters(f => ({ ...f, min_price: e.target.value }))} />
        </label>

        <label>
          Max Price
          <input type="number" value={filters.max_price} onChange={e => setFilters(f => ({ ...f, max_price: e.target.value }))} />
        </label>
      </aside>

      <main className="cpu-grid">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="pc-card" style={{ opacity: 0.4 }}>
              <div className="pc-card-image" style={{ background: "rgba(255,255,255,0.03)" }} />
              <div style={{ height: 14, background: "rgba(255,255,255,0.05)", borderRadius: 6 }} />
            </div>
          ))
        ) : rams.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No RAM found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          rams.map(ram => (
            <RamCard key={ram.product_id} ram={ram} onDetails={setSelected} onAdd={() => {}} />
          ))
        )}
      </main>

      <RamDetailsModal productId={selected} onClose={() => setSelected(null)} onAdd={() => {}} />
    </div>
  );
}
