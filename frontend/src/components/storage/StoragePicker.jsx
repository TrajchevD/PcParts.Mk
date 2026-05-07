import { useEffect, useState } from "react";
import { fetchStorage } from "../../api/storageProducts";
import StorageCard from "./StorageCard";
import StorageDetailsModal from "./StorageDetailsModal";

export default function StoragePicker({ onSelect }) {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);

  const [filters, setFilters] = useState({
    type: "",
    capacity_gb: "",
  });

  useEffect(() => {
    fetchStorage(filters).then(setItems);
  }, [filters]);

  return (
    <div className="cpu-page">
      <aside className="cpu-filters">
        <h3>Storage</h3>

        <label>
          Type
          <select onChange={e => setFilters(f => ({ ...f, type: e.target.value }))}>
            <option value="">All</option>
            <option value="NVMe">NVMe</option>
            <option value="SATA">SATA</option>
            <option value="HDD">HDD</option>
          </select>
        </label>

        <label>
          Min capacity (GB)
          <select onChange={e => setFilters(f => ({ ...f, capacity_gb: e.target.value }))}>
            <option value="">Any</option>
            <option value="500">500+</option>
            <option value="1000">1TB+</option>
            <option value="2000">2TB+</option>
          </select>
        </label>
      </aside>

      <main className="cpu-grid">
        {items.map(s => (
          <StorageCard
            key={s.product_id}
            storage={s}
            onDetails={setSelected}
            onAdd={() => onSelect(s.product_id)}
          />
        ))}
      </main>

      <StorageDetailsModal
        productId={selected}
        onClose={() => setSelected(null)}
        onAdd={(id) => {
          onSelect(id);
          setSelected(null);
        }}
      />
    </div>
  );
}
