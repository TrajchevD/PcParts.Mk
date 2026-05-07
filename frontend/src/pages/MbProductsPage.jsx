import { useEffect, useState } from "react";
import { fetchMotherboards } from "../api/mbProducts";
import MbCard from "../components/mb/MbCard";
import MbDetailsModal from "../components/mb/MbDetailsModal";

export default function MbProductsPage() {
  const [mbs, setMbs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMb, setSelectedMb] = useState(null);
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ socket: "", memory_type: "", form_factor: "", min_price: "", max_price: "" });

  useEffect(() => {
    setLoading(true);
    fetchMotherboards({ ...filters, sort }).then(setMbs).finally(() => setLoading(false));
  }, [filters, sort]);

  return (
    <div className="cpu-page">
      <aside className="cpu-filters">
        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          Motherboards <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Socket
          <select value={filters.socket} onChange={e => setFilters(f => ({ ...f, socket: e.target.value }))}>
            <option value="">All</option>
            <option value="AM4">AM4</option>
            <option value="AM5">AM5</option>
            <option value="LGA1700">LGA1700</option>
            <option value="LGA1851">LGA1851</option>
          </select>
        </label>

        <label>
          Memory Type
          <select value={filters.memory_type} onChange={e => setFilters(f => ({ ...f, memory_type: e.target.value }))}>
            <option value="">All</option>
            <option value="DDR4">DDR4</option>
            <option value="DDR5">DDR5</option>
          </select>
        </label>

        <label>
          Form Factor
          <select value={filters.form_factor} onChange={e => setFilters(f => ({ ...f, form_factor: e.target.value }))}>
            <option value="">All</option>
            <option value="mini-ITX">mini-ITX</option>
            <option value="mATX">mATX</option>
            <option value="ATX">ATX</option>
            <option value="E-ATX">E-ATX</option>
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
        ) : mbs.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No motherboards found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          mbs.map(mb => (
            <MbCard key={mb.product_id} mb={mb} onDetails={setSelectedMb} onAdd={() => {}} />
          ))
        )}
      </main>

      <MbDetailsModal productId={selectedMb} onClose={() => setSelectedMb(null)} />
    </div>
  );
}
