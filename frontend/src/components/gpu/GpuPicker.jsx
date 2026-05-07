import { useEffect, useState } from "react";
import { fetchGpus } from "../../api/gpuProducts";
import { getOptions } from "../../api/pcBuilder";
import GpuCard from "./GpuCard";
import GpuDetailsModal from "./GpuDetailsModal";

export default function GpuPicker({ onSelect, buildId }) {
  const [gpus, setGpus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGpu, setSelectedGpu] = useState(null);
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ brand: "", min_vram: "" });

  useEffect(() => {
    setLoading(true);
    const promise = buildId
      ? getOptions({
          build_id: buildId,
          slot: "gpu",
          sort,
          filters: {
            vram_gb: filters.min_vram ? Number(filters.min_vram) : undefined,
          },
        }).then(res => res.items)
      : fetchGpus({
          sort,
          filters: {
            brand:    filters.brand    || undefined,
            min_vram: filters.min_vram ? Number(filters.min_vram) : undefined,
          },
        });

    promise.then(setGpus).finally(() => setLoading(false));
  }, [filters, sort, buildId]);

  function handleAdd(gpu) {
    onSelect(buildId ? gpu.product_id : gpu.gpu_model);
  }

  return (
    <div className="cpu-page">
      <aside className="cpu-filters">
        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          GPUs <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Brand
          <select onChange={e => setFilters(f => ({ ...f, brand: e.target.value }))}>
            <option value="">All</option>
            <option value="NVIDIA">NVIDIA</option>
            <option value="AMD">AMD</option>
          </select>
        </label>

        <label>
          Min VRAM
          <select onChange={e => setFilters(f => ({ ...f, min_vram: e.target.value }))}>
            <option value="">Any</option>
            <option value="4">4 GB+</option>
            <option value="6">6 GB+</option>
            <option value="8">8 GB+</option>
            <option value="12">12 GB+</option>
            <option value="16">16 GB+</option>
          </select>
        </label>
      </aside>

      <main className="cpu-grid">
        {loading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="pc-card" style={{ opacity: 0.4 }}>
              <div className="pc-card-image" style={{ background: "rgba(255,255,255,0.03)" }} />
              <div style={{ height: 14, background: "rgba(255,255,255,0.05)", borderRadius: 6 }} />
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
              key={gpu.product_id ?? `${gpu.gpu_model}-${gpu.vram_gb}`}
              gpu={gpu}
              onDetails={() => setSelectedGpu({ model: gpu.gpu_model, vram: gpu.vram_gb })}
              onAdd={handleAdd}
            />
          ))
        )}
      </main>

      <GpuDetailsModal
        gpu={selectedGpu}
        onClose={() => setSelectedGpu(null)}
        onAdd={gpu => {
          const full = gpus.find(g => g.gpu_model === gpu.model) ?? { gpu_model: gpu.model };
          handleAdd(full);
          setSelectedGpu(null);
        }}
      />
    </div>
  );
}
