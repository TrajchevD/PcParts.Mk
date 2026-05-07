import { useEffect, useState } from "react";
import PartCard from "./PartCard";
import { getOptions } from "../../api/pcBuilder";

export default function PartsModelCpuTest({ slot, build, onClose, onSelect }) {
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({});
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sort, setSort] = useState("price_asc");

  useEffect(() => {
    if (slot === "cpu") {
      loadOptions();
    }
  }, [slot, search, filters, sort]);

  async function loadOptions() {
    setLoading(true);

    const res = await getOptions({
      build_id: build.build_id,
      slot: "cpu",
      search,
      filters,
      sort,
      limit: 20,
      offset: 0,
    });

    setOptions(res.items);
    setLoading(false);
  }

  // ❌ do nothing if not CPU (safe test)
  if (slot !== "cpu") return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        {/* HEADER */}
        <div className="modal-header">
          <h3>Select CPU</h3>
          <button onClick={onClose}>✕</button>
        </div>

        {/* BODY: LEFT FILTERS / RIGHT PRODUCTS */}
        <div className="modal-body">
          {/* LEFT: FILTERS */}
          <div className="filters-panel">
            <input
              placeholder="Search CPU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <div className="card">
              <label>
                Min cores
                <select
                  value={filters.min_cores || ""}
                  onChange={(e) =>
                    setFilters((f) => ({
                      ...f,
                      min_cores: e.target.value
                        ? Number(e.target.value)
                        : undefined,
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

              <label>
                Min price
                <input
                  type="number"
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

              <label>
                Sort by price
                <select
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                >
                  <option value="price_asc">Lowest price</option>
                  <option value="price_desc">Highest price</option>
                </select>
              </label>
            </div>
          </div>

          {/* RIGHT: PRODUCTS */}
          <div className="products-panel">
            {loading && <div>Loading...</div>}

            {!loading &&
              options.map((p) => (
                <PartCard
                  key={p.product_id}
                  part={p}
                  slot="cpu"
                  onSelect={onSelect}
                />
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}
