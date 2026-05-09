import { useEffect, useState } from "react";
import { fetchStorage } from "../api/storageProducts";
import StorageCard from "../components/storage/StorageCard";
import StorageDetailsModal from "../components/storage/StorageDetailsModal";
import CategoryNav from "../components/CategoryNav";

export default function StorageProductsPage({ onSelect }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ type: "", capacity_gb: "" });

  useEffect(() => {
    setLoading(true);
    fetchStorage({ ...filters, sort }).then(setItems).finally(() => setLoading(false));
  }, [filters, sort]);

  const handleAdd = onSelect ? (id) => onSelect(id) : () => {};

  return (
    <div className="cpu-page">
      <CategoryNav />
      <aside className="cpu-filters">
        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          Storage <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Type
          <select value={filters.type} onChange={e => setFilters(f => ({ ...f, type: e.target.value }))}>
            <option value="">All</option>
            <option value="NVMe">NVMe</option>
            <option value="SATA">SATA</option>
            <option value="HDD">HDD</option>
          </select>
        </label>

        <label>
          Min Capacity
          <select value={filters.capacity_gb} onChange={e => setFilters(f => ({ ...f, capacity_gb: e.target.value }))}>
            <option value="">Any</option>
            <option value="500">500 GB+</option>
            <option value="1000">1 TB+</option>
            <option value="2000">2 TB+</option>
          </select>
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
        ) : items.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No storage drives found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          items.map(s => (
            <StorageCard
              key={s.product_id}
              storage={s}
              onDetails={setSelected}
              onAdd={() => handleAdd(s.product_id)}
            />
          ))
        )}
      </main>

      <StorageDetailsModal
        productId={selected}
        onClose={() => setSelected(null)}
        onAdd={id => { handleAdd(id); setSelected(null); }}
      />
    </div>
  );
}
