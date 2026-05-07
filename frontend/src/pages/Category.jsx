import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchProducts } from "../api/products";
import ProductCard from "../components/ProductCard";
import AlertsPanel from "../alerts/AlertsPanel";
import NotificationsPanel from "../notifications/NotificationsPanel";
import { useAuth } from "../auth/AuthContext";

const STORES = ["", "Setec", "Anhoch", "Neptun", "Gjirafa50"];

export default function Category() {
  const { category } = useParams();
  const { token } = useAuth();

  /* ------------------ FILTER STATE ------------------ */
  const [q, setQ] = useState("");
  const [store, setStore] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [sort, setSort] = useState("price_asc");

  /* ------------------ UI STATE ------------------ */
  const [activePanel, setActivePanel] = useState(null); 
  // null | "filters" | "alerts" | "notifications"

  const [page, setPage] = useState(1);
  const limit = 24;

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [result, setResult] = useState(null);

  /* ------------------ PARAMS ------------------ */
  const params = useMemo(() => ({
    category,
    q: q.trim() || undefined,
    store: store || undefined,
    price_min: priceMin === "" ? undefined : Number(priceMin),
    price_max: priceMax === "" ? undefined : Number(priceMax),
    sort,
    page,
    limit,
  }), [category, q, store, priceMin, priceMax, sort, page]);

  /* ------------------ FETCH ------------------ */
  function load() {
    setLoading(true);
    setErr("");

    fetchProducts(params)
      .then(setResult)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  }

  /* Load on category or page change ONLY */
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, page]);

  /* Reset filters on category change */
  useEffect(() => {
    setQ("");
    setStore("");
    setPriceMin("");
    setPriceMax("");
    setSort("price_asc");
    setPage(1);
    setActivePanel(null);
  }, [category]);

  const items = result?.items || [];
  const pages = result?.pages || 1;

  /* ------------------ PANEL TOGGLE ------------------ */
  function togglePanel(panel) {
    setActivePanel((curr) => (curr === panel ? null : panel));
  }

  /* ------------------ RENDER ------------------ */
  return (
    <div>
      {/* HEADER */}
      <div className="row" style={{ marginBottom: 12 }}>
        <div>
          <h2 style={{ margin: 0 }}>Category: {category}</h2>
          <div className="muted" style={{ marginTop: 6 }}>
            <Link to="/" className="muted" style={{ textDecoration: "underline" }}>
              ← back to categories
            </Link>
          </div>
        </div>

        <div className="pill">
          {result ? `${result.total} results` : "…"}
        </div>
      </div>

      {/* PANEL BUTTON BAR */}
      <div className="panelBar">
        <button
          className={activePanel === "filters" ? "active" : ""}
          onClick={() => togglePanel("filters")}
        >
          Filters
        </button>

        <button
          className={activePanel === "alerts" ? "active" : ""}
          onClick={() => togglePanel("alerts")}
        >
          Alerts
        </button>

        <button
          className={activePanel === "notifications" ? "active" : ""}
          onClick={() => togglePanel("notifications")}
        >
          Notifications
        </button>
      </div>

      {/* FILTERS PANEL */}
      {activePanel === "filters" && (
        <div className="card panel">
          <div className="controls">
            <div>
              <label>Search</label>
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="e.g. 4060, Ryzen, Kingston..."
              />
            </div>

            <div>
              <label>Store</label>
              <select value={store} onChange={(e) => setStore(e.target.value)}>
                {STORES.map((s) => (
                  <option key={s} value={s}>
                    {s === "" ? "All stores" : s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Price min</label>
              <input
                type="number"
                value={priceMin}
                onChange={(e) => setPriceMin(e.target.value)}
              />
            </div>

            <div>
              <label>Price max</label>
              <input
                type="number"
                value={priceMax}
                onChange={(e) => setPriceMax(e.target.value)}
              />
            </div>

            <div>
              <label>Sort</label>
              <select value={sort} onChange={(e) => setSort(e.target.value)}>
                <option value="price_asc">Price ↑</option>
                <option value="price_desc">Price ↓</option>
                <option value="newest">Newest</option>
                <option value="title_asc">Title A-Z</option>
                <option value="title_desc">Title Z-A</option>
              </select>
            </div>
          </div>

          <div className="panelActions">
            <button
              className="primary"
              onClick={() => {
                setPage(1);
                load();
                setActivePanel(null);
              }}
            >
              Apply filters
            </button>
          </div>
        </div>
      )}

      {/* ALERTS PANEL */}
      {activePanel === "alerts" && (
        <div className="card panel">
          {token ? <AlertsPanel /> : <p>Login required to use alerts</p>}
        </div>
      )}

      {/* NOTIFICATIONS PANEL */}
      {activePanel === "notifications" && (
        <div className="card panel">
          {token ? <NotificationsPanel /> : <p>Login required to view notifications</p>}
        </div>
      )}

      {/* ERRORS */}
      {err && (
        <div className="card" style={{ marginTop: 14, borderColor: "rgba(255,0,0,0.25)" }}>
          <div style={{ fontWeight: 700 }}>API error</div>
          <div className="muted">{err}</div>
        </div>
      )}

      {/* NO RESULTS */}
      {!err && !loading && items.length === 0 && (
        <div className="card" style={{ marginTop: 14 }}>
          <div style={{ fontWeight: 700 }}>No results</div>
          <div className="muted">Try removing filters or changing search.</div>
        </div>
      )}

      {/* PRODUCTS */}
      <div className="products">
        {items.map((p) => (
          <ProductCard key={p.id} p={p} />
        ))}
      </div>

      {/* PAGINATION */}
      <div className="pagination">
        <button
          onClick={() => setPage((x) => Math.max(1, x - 1))}
          disabled={page <= 1 || loading}
        >
          ← Prev
        </button>

        <div className="pill">
          Page {page} / {pages}
        </div>

        <button
          onClick={() => setPage((x) => Math.min(pages, x + 1))}
          disabled={page >= pages || loading}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
