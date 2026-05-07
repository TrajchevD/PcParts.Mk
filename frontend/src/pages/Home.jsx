import { useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import { createBuild } from "../api/buildManager";

const CATEGORIES = ["All", "CPU", "GPU", "MB", "RAM", "Storage"];

const DEMO_CARDS = [
  {
    category: "CPU",
    name: "AMD Ryzen 7 9800X3D",
    badges: [{ label: "AM5", cls: "mob-badge-cyan" }, { label: "DDR5", cls: "mob-badge-purple" }],
    specs: [
      { k: "Cores", v: "8" }, { k: "L3 Cache", v: "96MB" },
      { k: "TDP",   v: "120W" }, { k: "Socket", v: "AM5" },
    ],
    price: "35,999",
    stores: [
      { init: "A", avail: true }, { init: "S", avail: true },
      { init: "N", avail: false }, { init: "G", avail: false },
    ],
    route: "/catalog/cpu",
  },
  {
    category: "CPU",
    name: "Intel Core i9-14900K",
    badges: [{ label: "LGA1700", cls: "mob-badge-orange" }, { label: "DDR5", cls: "mob-badge-purple" }],
    specs: [
      { k: "Cores", v: "24" }, { k: "L3 Cache", v: "36MB" },
      { k: "TDP",   v: "125W" }, { k: "Socket", v: "LGA1700" },
    ],
    price: "27,990",
    stores: [
      { init: "A", avail: true }, { init: "S", avail: true },
      { init: "N", avail: true }, { init: "G", avail: false },
    ],
    route: "/catalog/cpu",
  },
];

export default function Home() {
  const navigate = useNavigate();
  const { toggleSidebar } = useOutletContext() || {};
  const [creating, setCreating] = useState(false);
  const [activeCategory, setActiveCategory] = useState("All");

  async function handleStartBuilding() {
    if (creating) return;
    setCreating(true);
    try {
      const data = await createBuild("My Build");
      navigate(`/builder-v2/${data.build_id}`);
    } catch {
      navigate("/builds");
    } finally {
      setCreating(false);
    }
  }

  return (
    <>
      {/* ── DESKTOP ── */}
      <div className="cyber-home dsk-only">
        <section className="cyber-hero">
          <div className="hero-glow" />
          <img src="/logos/gpu_v2.png"     alt="GPU"         className="floating gpu" />
          <img src="/logos/mb_v2.png"      alt="Motherboard" className="floating motherboard" />
          <img src="/logos/cpu_v2.png"     alt="CPU"         className="floating cpu" />
          <img src="/logos/ram_v2.png"     alt="RAM"         className="floating ram" />
          <img src="/logos/storage_v2.png" alt="Storage"     className="floating storage" />
          <div className="hero-content">
            <h1 className="cyber-title">
              BUILD YOUR PC <br />
              <span>THE SMART WAY</span>
            </h1>
            <p className="cyber-subtitle">
              Real-time compatibility · Live price comparison from Macedonian stores · AI-powered build recommendations
            </p>
            <div className="cyber-buttons">
              <button className="btn-neon" onClick={handleStartBuilding} disabled={creating}>
                {creating ? "Creating…" : "⚡ Start Building"}
              </button>
              <Link to="/catalog/gpu" className="btn-outline-neon">Browse Parts</Link>
            </div>
          </div>
        </section>
        <section className="cyber-categories">
          <h2 className="section-heading">Popular Build Profiles</h2>
          <div className="cyber-grid">
            <div className="cyber-card red" onClick={() => navigate("/recommend")}>
              <h3>🔴 All-AMD Red Beast</h3>
              <p>Maximum performance per denar. Ryzen + Radeon combo.</p>
            </div>
            <div className="cyber-card white" onClick={() => navigate("/recommend")}>
              <h3>🤍 Balanced Mid-Range</h3>
              <p>Clean aesthetics, smooth 1080p / 1440p gaming.</p>
            </div>
            <div className="cyber-card blue" onClick={() => navigate("/recommend")}>
              <h3>🔵 E-Sports Build</h3>
              <p>High FPS, low latency — built for competitive play.</p>
            </div>
          </div>
        </section>
      </div>

      {/* ── MOBILE ── */}
      <div className="mob-home mob-only">
        {/* Top bar */}
        <div className="mob-topbar">
          <span className="mob-brand">
            PC<span className="mob-brand-accent">Parts</span>MK
          </span>
          <div className="mob-topbar-right">
            <button className="mob-icon-btn">🔔</button>
            <button className="mob-icon-btn" onClick={toggleSidebar}>☰</button>
          </div>
        </div>

        {/* Hero */}
        <div className="mob-hero">
          <div className="mob-eyebrow">
            <span className="mob-eyebrow-line" />
            <span>Macedonia's parts aggregator</span>
          </div>
          <h1 className="mob-hero-h1">
            Find the <br /><span>best price.</span>
          </h1>
          <p className="mob-hero-sub">
            Real-time prices from all major Macedonian PC stores in one place.
          </p>
          <div className="mob-hero-btns">
            <button className="mob-btn-accent" onClick={handleStartBuilding} disabled={creating}>
              {creating ? "Creating…" : "Build a PC"}
            </button>
            <Link to="/catalog/gpu" className="mob-btn-outline">Browse</Link>
          </div>
        </div>

        {/* Stats strip */}
        <div className="mob-stats-strip">
          <div className="mob-stat-cell">
            <div className="mob-stat-num">2K<span>+</span></div>
            <div className="mob-stat-label">Products</div>
          </div>
          <div className="mob-stat-cell">
            <div className="mob-stat-num">4</div>
            <div className="mob-stat-label">Stores</div>
          </div>
          <div className="mob-stat-cell">
            <div className="mob-stat-num">Daily</div>
            <div className="mob-stat-label">Updates</div>
          </div>
        </div>

        {/* Search bar */}
        <div className="mob-search-bar">
          <span>🔍</span>
          <input type="text" placeholder="Search parts…" />
        </div>

        {/* Category pills */}
        <div className="mob-pills-scroll">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              className={`mob-pill${activeCategory === cat ? " mob-pill-active" : ""}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Section header */}
        <div className="mob-section-header">
          <span className="mob-section-title">Top CPUs</span>
          <Link to="/catalog/cpu" className="mob-see-all">See all →</Link>
        </div>

        {/* Product cards */}
        {DEMO_CARDS.map((card, i) => (
          <div key={i} className="mob-product-card">
            <div className="mob-card-top">
              <div className="mob-card-info">
                <span className="mob-card-category">{card.category}</span>
                <span className="mob-card-name">{card.name}</span>
              </div>
              <div className="mob-card-badges">
                {card.badges.map(b => (
                  <span key={b.label} className={`mob-badge ${b.cls}`}>{b.label}</span>
                ))}
              </div>
            </div>
            <div className="mob-card-specs">
              {card.specs.map(s => (
                <div key={s.k} className="mob-spec-item">
                  <span className="mob-spec-k">{s.k}</span>
                  <span className="mob-spec-v">{s.v}</span>
                </div>
              ))}
            </div>
            <div className="mob-card-bottom">
              <div className="mob-card-bottom-left">
                <div className="mob-price">
                  {card.price}<span className="mob-price-currency"> ден</span>
                </div>
                <div className="mob-store-dots">
                  {card.stores.map(s => (
                    <span
                      key={s.init}
                      className={`mob-store-dot ${s.avail ? "mob-store-avail" : "mob-store-na"}`}
                    >
                      {s.init}
                    </span>
                  ))}
                </div>
              </div>
              <div className="mob-card-actions">
                <button className="mob-card-btn mob-card-btn-muted">Compare</button>
                <button className="mob-card-btn mob-card-btn-accent">+ Build</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
