import { useEffect, useState } from "react";
import { fetchCpus } from "../../api/cpuProducts";
import { getOptions } from "../../api/pcBuilder";
import CpuCard from "./CpuCard";
import CpuDetailsModal from "./CpuDetailsModal";

export default function CpuPicker({ onSelect, buildId }) {
  const [cpus, setCpus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCpu, setSelectedCpu] = useState(null);
  const [error, setError] = useState("");
  const [sort, setSort] = useState("price_asc");
  const [filters, setFilters] = useState({ brand: "", socket: "", min_cores: "" });

  useEffect(() => {
    setLoading(true);
    const promise = buildId
      ? getOptions({
          build_id: buildId,
          slot: "cpu",
          sort,
          filters: {
            brand: filters.brand || undefined,
            socket: filters.socket || undefined,
            cores: filters.min_cores ? Number(filters.min_cores) : undefined,
          },
        }).then(res => res.items)
      : fetchCpus({ ...filters, sort });

    promise.then(setCpus).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [filters, sort, buildId]);

  async function handleAdd(cpu) {
    setError("");
    try {
      await onSelect(buildId ? cpu.product_id : cpu.cpu_model);
    } catch (err) {
      setError(err.message || "Failed to add CPU.");
    }
  }

  return (
    <div className="cpu-page">
      <aside className="cpu-filters">
        {error && <div className="compat-error">⚠️ {error}</div>}

        <h3 onClick={() => setSort(s => s === "price_asc" ? "price_desc" : "price_asc")}>
          CPUs <span>{sort === "price_asc" ? "↑" : "↓"}</span>
        </h3>

        <label>
          Brand
          <select onChange={e => setFilters(f => ({ ...f, brand: e.target.value }))}>
            <option value="">All</option>
            <option value="AMD">AMD</option>
            <option value="Intel">Intel</option>
          </select>
        </label>

        <label>
          Socket
          <select onChange={e => setFilters(f => ({ ...f, socket: e.target.value }))}>
            <option value="">All</option>
            <option value="AM4">AM4</option>
            <option value="AM5">AM5</option>
            <option value="LGA1700">LGA1700</option>
          </select>
        </label>

        <label>
          Min Cores
          <select onChange={e => setFilters(f => ({ ...f, min_cores: e.target.value }))}>
            <option value="">Any</option>
            <option value="4">4+</option>
            <option value="6">6+</option>
            <option value="8">8+</option>
            <option value="12">12+</option>
            <option value="16">16+</option>
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
        ) : cpus.length === 0 ? (
          <div className="empty-state" style={{ gridColumn: "1/-1" }}>
            <span className="empty-icon">🔍</span>
            <h3>No CPUs found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          cpus.map(cpu => (
            <CpuCard
              key={cpu.product_id ?? cpu.cpu_model}
              cpu={cpu}
              onAdd={handleAdd}
              onDetails={() => setSelectedCpu(cpu.cpu_model)}
            />
          ))
        )}
      </main>

      <CpuDetailsModal
        cpuModel={selectedCpu}
        onClose={() => setSelectedCpu(null)}
        onAdd={async model => {
          const cpu = cpus.find(c => c.cpu_model === model) ?? { cpu_model: model };
          await handleAdd(cpu);
          setSelectedCpu(null);
        }}
      />
    </div>
  );
}
