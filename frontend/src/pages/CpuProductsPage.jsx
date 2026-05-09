import { useEffect, useState } from "react";
import { fetchCpus } from "../api/cpuProducts";
import CpuCard from "../components/cpu/CpuCard";
import CpuDetailsModal from "../components/cpu/CpuDetailsModal";
import CategoryNav from "../components/CategoryNav";

export default function CpuProductsPage() {
  const [cpus, setCpus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCpu, setSelectedCpu] = useState(null);
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ brand: "", socket: "", min_cores: "", min_price: "", max_price: "" });

  useEffect(() => {
    setLoading(true);
    fetchCpus({ ...filters, sort })
      .then(setCpus)
      .finally(() => setLoading(false));
  }, [filters, sort]);

  return (
    <div className="cpu-page">
      <CategoryNav />
      <aside className="cpu-filters">
        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          CPUs <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Brand
          <select value={filters.brand} onChange={e => setFilters(f => ({ ...f, brand: e.target.value }))}>
            <option value="">All</option>
            <option value="AMD">AMD</option>
            <option value="Intel">Intel</option>
          </select>
        </label>

        <label>
          Socket
          <select value={filters.socket} onChange={e => setFilters(f => ({ ...f, socket: e.target.value }))}>
            <option value="">All</option>
            <option value="AM4">AM4</option>
            <option value="AM5">AM5</option>
            <option value="LGA1700">LGA1700</option>
          </select>
        </label>

        <label>
          Min Cores
          <select value={filters.min_cores || ""} onChange={e => setFilters(f => ({ ...f, min_cores: e.target.value ? Number(e.target.value) : "" }))}>
            <option value="">Any</option>
            <option value="4">4+</option>
            <option value="6">6+</option>
            <option value="8">8+</option>
            <option value="12">12+</option>
            <option value="16">16+</option>
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
              <div style={{ height: 10, background: "rgba(255,255,255,0.03)", borderRadius: 6, width: "60%" }} />
            </div>
          ))
        ) : cpus.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No CPUs found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          cpus.map(cpu => (
            <CpuCard key={cpu.cpu_model} cpu={cpu} onDetails={setSelectedCpu} onAdd={() => {}} />
          ))
        )}
      </main>

      <CpuDetailsModal cpuModel={selectedCpu} onClose={() => setSelectedCpu(null)} />
    </div>
  );
}
