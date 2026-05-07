export default function CpuFilters({ filters, setFilters }) {
  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <h4>CPU Filters</h4>

      {/* CORES */}
      <label>
        Min cores
        <select
          value={filters.cores || ""}
          onChange={(e) =>
            setFilters((f) => ({
              ...f,
              cores: e.target.value ? Number(e.target.value) : undefined,
            }))
          }
        >
          <option value="">Any</option>
          <option value="4">4+</option>
          <option value="6">6+</option>
          <option value="8">8+</option>
          <option value="12">12+</option>
          <option value="16">16+</option>
        </select>
      </label>

      {/* PRICE */}
      <div style={{ display: "flex", gap: 8 }}>
        <label>
          Min price
          <input
            type="number"
            value={filters.min_price || ""}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                min_price: e.target.value
                  ? Number(e.target.value)
                  : undefined,
              }))
            }
          />
        </label>

        <label>
          Max price
          <input
            type="number"
            value={filters.max_price || ""}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                max_price: e.target.value
                  ? Number(e.target.value)
                  : undefined,
              }))
            }
          />
        </label>
      </div>
    </div>
  );
}
