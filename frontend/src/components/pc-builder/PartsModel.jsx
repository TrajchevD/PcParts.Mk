// import { useEffect, useState } from "react";
// import { getOptions } from "../../api/pcBuilder";
// import PartCard from "./PartCard";

// export default function PartsModel({ slot, build, onClose, onSelect }) {
//   const [search, setSearch] = useState("");
//   const [options, setOptions] = useState([]);
//   const [loading, setLoading] = useState(false);

//   useEffect(() => {
//     loadOptions();
//   }, [slot]);

//   async function loadOptions() {
//     setLoading(true);
//     const res = await getOptions({
//       slot,
//       search,
//       constraints: build.constraints,
//     });
//     setOptions(res.items);
//     setLoading(false);
//   }

//   return (
//     <div className="modal-overlay">
//       <div className="modal">
//         {/* HEADER */}
//         <div className="modal-header">
//           <h3>Select {slot.toUpperCase()}</h3>
//           <button onClick={onClose}>✕</button>
//         </div>

//         {/* SEARCH */}
//         <input
//           placeholder={`Search ${slot}...`}
//           value={search}
//           onChange={(e) => setSearch(e.target.value)}
//           onKeyDown={(e) => e.key === "Enter" && loadOptions()}
//         />

//         {/* LIST */}
//         <div className="parts-list">
//           {loading && <div>Loading...</div>}

//           {!loading &&
//             options.map((p) => (
//               <PartCard
//                 key={p.product_id}
//                 part={p}
//                 slot={slot}
//                 onSelect={onSelect}
//               />
//             ))}
//         </div>
//       </div>
//     </div>
//   );
// }
import { useEffect, useState } from "react";
import PartCard from "./PartCard";
import { getOptions, getMbSockets } from "../../api/pcBuilder";

export default function PartsModel({ slot, build, onClose, onSelect }) {
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({});
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mbSocketOptions, setMbSocketOptions] = useState([]);
  const [sort, setSort] = useState("price_asc");

  useEffect(() => {
  if (slot === "mb") {
    getMbSockets().then(setMbSocketOptions);
  }
}, [slot]);

useEffect(() => {
  loadOptions();
}, [slot, search, filters, sort]);


  async function loadOptions() {
    setLoading(true);
    const res = await getOptions({
      build_id: build.build_id,   // ✅ CRITICAL
      slot,
      search,
      filters,
      sort,               // ✅ CPU filters go here
      limit: 20,
      offset: 0,
    });
    setOptions(res.items);
    setLoading(false);
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        {/* HEADER */}
        <div className="modal-header">
          <h3>Select {slot.toUpperCase()}</h3>
          <button onClick={onClose}>✕</button>
        </div>

        {/* SEARCH */}
        <input
          placeholder={`Search ${slot}...`}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* ✅ CPU FILTERS */}
        {slot === "cpu" && (
          <div className="card" style={{ marginBottom: 10 }}>
            <label>
              Min cores
              <select
                value={filters.cores || ""}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    cores: e.target.value
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
              {/* <select
                value={filters.sort || "price_asc"}
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    sort: e.target.value,
                  }))
                }
              >
                <option value="price_asc">Lowest price</option>
                <option value="price_desc">Highest price</option>
              </select> */}
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
              >
                <option value="price_asc">Lowest price</option>
                <option value="price_desc">Highest price</option>
              </select>

            </label>
          </div>
        )}

        {slot === "mb" && (
          <div className="card">
            <label>
              Socket
              <select
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    socket: e.target.value || undefined,
                  }))
                }
              >
                <option value="">Any</option>
                {mbSocketOptions.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </label>
              
            <label>
              Form factor
              <select
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    form_factor: e.target.value || undefined,
                  }))
                }
              >
                <option value="">Any</option>
                <option value="ATX">ATX</option>
                <option value="Micro-ATX">Micro-ATX</option>
                <option value="Mini-ITX">Mini-ITX</option>
              </select>
            </label>
              
            <label>
              Memory slots
              <select
                onChange={(e) =>
                  setFilters((f) => ({
                    ...f,
                    memory_slots: e.target.value
                      ? Number(e.target.value)
                      : undefined,
                  }))
                }
              >
                <option value="">Any</option>
                <option value="2">2+</option>
                <option value="4">4</option>
              </select>
            </label>
            <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
              >
                <option value="price_asc">Lowest price</option>
                <option value="price_desc">Highest price</option>
              </select>
          </div>
        )}

        {slot === "ram" && (
  <div className="card">
    <label>
      Min capacity (GB)
      <select
        onChange={(e) =>
          setFilters(f => ({
            ...f,
            capacity_gb: e.target.value
              ? Number(e.target.value)
              : undefined
          }))
        }
      >
        <option value="">Any</option>
        <option value="8">8+</option>
        <option value="16">16+</option>
        <option value="32">32+</option>
        <option value="64">64+</option>
      </select>
    </label>

    <label>
      Sort by price
      <select value={sort} onChange={(e) => setSort(e.target.value)}>
        <option value="price_asc">Lowest price</option>
        <option value="price_desc">Highest price</option>
      </select>
    </label>
  </div>
)}

{slot === "gpu" && (
  <div className="card">
    <label>
      Min VRAM (GB)
      <select
        onChange={(e) =>
          setFilters(f => ({
            ...f,
            vram_gb: e.target.value
              ? Number(e.target.value)
              : undefined
          }))
        }
      >
        <option value="">Any</option>
        <option value="6">6+</option>
        <option value="8">8+</option>
        <option value="12">12+</option>
        <option value="16">16+</option>
      </select>
    </label>

    <label>
      Sort by price
      <select value={sort} onChange={(e) => setSort(e.target.value)}>
        <option value="price_asc">Lowest price</option>
        <option value="price_desc">Highest price</option>
      </select>
    </label>
  </div>
)}

{slot === "storage" && (
  <div className="card">
    <label>
      Min capacity (GB)
      <select
        onChange={(e) =>
          setFilters(f => ({
            ...f,
            capacity_gb: e.target.value
              ? Number(e.target.value)
              : undefined
          }))
        }
      >
        <option value="">Any</option>
        <option value="256">256+</option>
        <option value="512">512+</option>
        <option value="1024">1TB+</option>
        <option value="2048">2TB+</option>
      </select>
    </label>

    <label>
      Interface
      <select
        onChange={(e) =>
          setFilters(f => ({
            ...f,
            interface: e.target.value || undefined
          }))
        }
      >
        <option value="">Any</option>
        <option value="NVMe">NVMe</option>
        <option value="SATA">SATA</option>
      </select>
    </label>

    <label>
      Sort by price
      <select value={sort} onChange={(e) => setSort(e.target.value)}>
        <option value="price_asc">Lowest price</option>
        <option value="price_desc">Highest price</option>
      </select>
    </label>
  </div>
)}


        {/* LIST */}
        <div className="parts-list">
          {loading && <div>Loading...</div>}
          {!loading &&
            options.map((p) => (
              <PartCard
                key={p.product_id}
                part={p}
                slot={slot}
                onSelect={onSelect}
              />
            ))}
        </div>
      </div>
    </div>
  );
}
