import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchGpus } from "../api/gpuProducts";
import GpuCard from "../components/gpu/GpuCard";
import GpuDetailsModal from "../components/gpu/GpuDetailsModal";
import MobileNavBar from "../components/MobileNavBar";

export default function GpuProductsPage() {
  const [searchParams] = useSearchParams();
  const [gpus, setGpus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGpu, setSelectedGpu] = useState(null);
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ brand: "", min_vram: "", min_price: "", max_price: "" });
  const [search, setSearch] = useState(searchParams.get("q") || "");

  useEffect(() => { setSearch(searchParams.get("q") || ""); }, [searchParams]);

  useEffect(() => {
    setLoading(true);
    fetchGpus({
      sort,
      search: search || undefined,
      filters: {
        brand:     filters.brand     || undefined,
        min_vram:  filters.min_vram  ? Number(filters.min_vram) : undefined,
        min_price: filters.min_price || undefined,
        max_price: filters.max_price || undefined,
      },
    }).then(setGpus).finally(() => setLoading(false));
  }, [filters, sort, search]);

  return (
    <div className="cpu-page">
      <MobileNavBar title="GPUs" />
      <aside className="cpu-filters">
        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          GPUs <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Search
          <input type="text" placeholder="e.g. RTX 4070" value={search} onChange={e => setSearch(e.target.value)} />
        </label>

        <label>
          Brand
          <select value={filters.brand} onChange={e => setFilters(f => ({ ...f, brand: e.target.value }))}>
            <option value="">All</option>
            <option value="NVIDIA">NVIDIA</option>
            <option value="AMD">AMD</option>
          </select>
        </label>

        <label>
          Min VRAM
          <select value={filters.min_vram} onChange={e => setFilters(f => ({ ...f, min_vram: e.target.value }))}>
            <option value="">Any</option>
            <option value="4">4 GB+</option>
            <option value="6">6 GB+</option>
            <option value="8">8 GB+</option>
            <option value="12">12 GB+</option>
            <option value="16">16 GB+</option>
            <option value="24">24 GB+</option>
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
        ) : gpus.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No GPUs found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          gpus.map(gpu => (
            <GpuCard
              key={`${gpu.gpu_model}-${gpu.vram_gb}`}
              gpu={gpu}
              onDetails={() => setSelectedGpu({ model: gpu.gpu_model, vram: gpu.vram_gb })}
              onAdd={() => {}}
            />
          ))
        )}
      </main>

      <GpuDetailsModal gpu={selectedGpu} onClose={() => setSelectedGpu(null)} />
    </div>
  );
}
