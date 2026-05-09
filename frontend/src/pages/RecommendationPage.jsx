import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { recommendBuild } from "../api/recommendationApi";
import RecommendationBuildView from "../components/recommendation/RecommendationBuildView";

const USE_CASE_MAP = { Gaming: "aaa", Workstation: "aaa", Office: "school", Streaming: "esports" };
const USE_CASES   = ["Gaming", "Workstation", "Office", "Streaming"];

const PART_ICONS  = { cpu: "⬡", gpu: "▣", ram: "≡", mb: "⊞", storage: "◧" };
const PART_LABELS = { cpu: "CPU", gpu: "GPU", ram: "RAM", mb: "Motherboard", storage: "Storage" };

function getPartName(value) {
  if (!value) return "—";
  return value.model || value.cpu_model || value.gpu_model || value.mb_model || value.series || JSON.stringify(value);
}

function MobRecCard({ title, data, badge, badgeCls, borderColor }) {
  if (!data) return null;
  const { build, total_price } = data;

  return (
    <div className="mob-rec-card" style={borderColor ? { borderColor } : {}}>
      <div className="mob-rec-card-header">
        <span className="mob-rec-card-title">{title}</span>
        <span className={`mob-score-badge ${badgeCls}`}>{badge}</span>
      </div>
      <div className="mob-rec-parts">
        {Object.entries(build).map(([key, value]) => {
          if (!value) return null;

          if (key === "recommended_psu_w") {
            return (
              <div key={key} className="mob-rec-part-row">
                <span className="mob-rec-part-icon">⚡</span>
                <div className="mob-rec-part-info">
                  <span className="mob-rec-part-cat">PSU</span>
                  <span className="mob-rec-part-name">{value}W recommended</span>
                </div>
              </div>
            );
          }

          const name  = getPartName(value);
          const price = value.min_price;
          return (
            <div key={key} className="mob-rec-part-row">
              <span className="mob-rec-part-icon">{PART_ICONS[key] || "·"}</span>
              <div className="mob-rec-part-info">
                <span className="mob-rec-part-cat">{PART_LABELS[key] || key.toUpperCase()}</span>
                <span className="mob-rec-part-name">{name}</span>
              </div>
              {price != null && (
                <span className="mob-rec-part-price">{price.toLocaleString()}</span>
              )}
            </div>
          );
        })}
      </div>
      <div className="mob-rec-card-bottom">
        <div className="mob-rec-total-lbl">Total</div>
        <div className="mob-rec-total-price">
          {total_price?.toLocaleString()} <span className="mob-rec-total-den">ден</span>
        </div>
      </div>
    </div>
  );
}

export default function RecommendationPage() {
  const { toggleSidebar } = useOutletContext() || {};
  const [budget, setBudget]   = useState(100000);
  const [profile, setProfile] = useState("aaa");
  const [useCase, setUseCase] = useState("Gaming");
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  async function handleGenerate() {
    if (loading) return;
    setError("");
    setLoading(true);
    try {
      const r = await recommendBuild(budget, profile);
      setResult(r);
    } catch (e) {
      setError(e.message || "Failed to generate recommendation.");
    } finally {
      setLoading(false);
    }
  }

  function handleUseCaseChange(uc) {
    setUseCase(uc);
    setProfile(USE_CASE_MAP[uc] || "aaa");
  }

  return (
    <>
      {/* ── DESKTOP ── */}
      <div className="recommend-page dsk-only">
        <h2>AI Build Recommendation</h2>
        <p className="muted" style={{ marginBottom: 0 }}>
          Generates two compatible builds (Intel + AMD) and compares value scores.
        </p>
        <div className="recommend-controls">
          <label style={{ flexDirection: "column" }}>
            Budget (MKD)
            <input
              type="number"
              value={budget}
              min={10000}
              max={500000}
              step={5000}
              onChange={e => setBudget(Number(e.target.value))}
            />
          </label>
          <label style={{ flexDirection: "column" }}>
            Profile
            <select value={profile} onChange={e => setProfile(e.target.value)}>
              <option value="esports">⚡ E-Sports</option>
              <option value="aaa">🎮 AAA Gaming</option>
              <option value="school">📚 School / Office</option>
            </select>
          </label>
          <button
            className="btn-primary"
            style={{ alignSelf: "flex-end" }}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? <><span className="loading-spinner" /> Generating…</> : "Generate"}
          </button>
          {result?.winner && (
            <div className="winner-badge">Winner: {result.winner.toUpperCase()}</div>
          )}
        </div>
        {error && <div className="compat-error">⚠️ {error}</div>}
        {result?.error === "budget_too_low" && (
          <div className="compat-error">
            ⚠️ Budget too low for any complete build. Minimum recommended: {result.minimum_budget?.toLocaleString()} MKD
          </div>
        )}
        {result && !result.error && (
          <div className="recommend-builds">
            <RecommendationBuildView title="Intel Build" data={result.intel} highlight={result.winner === "intel"} />
            <RecommendationBuildView title="AMD Build"   data={result.amd}   highlight={result.winner === "amd"} />
          </div>
        )}
        {!result && !loading && (
          <div className="empty-state" style={{ marginTop: 48 }}>
            <span className="empty-icon">🤖</span>
            <h3>No recommendation yet</h3>
            <p>Set your budget and profile, then click Generate.</p>
          </div>
        )}
      </div>

      {/* ── MOBILE ── */}
      <div className="mob-recs mob-only">
        {/* Top bar */}
        <div className="mob-topbar">
          <span className="mob-page-title">Recommendations</span>
          <button
            className="mob-icon-btn mob-icon-btn-accent"
            onClick={handleGenerate}
            disabled={loading}
            title="Refresh"
          >
            ↺
          </button>
        </div>

        {/* Form */}
        <div className="mob-recs-form">
          {/* Use case */}
          <div className="mob-form-group">
            <span className="mob-form-label">Use Case</span>
            <div className="mob-chips">
              {USE_CASES.map(uc => (
                <button
                  key={uc}
                  className={`mob-chip${useCase === uc ? " mob-chip-active" : ""}`}
                  onClick={() => handleUseCaseChange(uc)}
                >
                  {uc}
                </button>
              ))}
            </div>
          </div>

          {/* Budget */}
          <div className="mob-form-group">
            <span className="mob-form-label">Budget</span>
            <div className="mob-budget-val">
              {budget.toLocaleString()} <span className="mob-budget-den">ден</span>
            </div>
            <input
              type="range"
              className="mob-range"
              min={20000}
              max={300000}
              step={5000}
              value={budget}
              onChange={e => setBudget(Number(e.target.value))}
            />
            <div className="mob-range-labels">
              <span>20K</span>
              <span>300K</span>
            </div>
          </div>

          {/* Generate */}
          <button
            className="mob-generate-btn"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating…" : "Generate Builds ✦"}
          </button>
        </div>

        {error && (
          <div className="compat-error" style={{ margin: "0 16px 8px" }}>⚠️ {error}</div>
        )}
        {result?.error === "budget_too_low" && (
          <div className="compat-error" style={{ margin: "0 16px 8px" }}>
            ⚠️ Budget too low. Minimum: {result.minimum_budget?.toLocaleString()} ден
          </div>
        )}

        <div className="mob-divider" />

        {/* Results */}
        <div className="mob-results-header">Results</div>

        {result && !result.error ? (
          <>
            {result.intel && (
              <MobRecCard
                title="Intel Build"
                data={result.intel}
                badge={result.winner === "intel" ? "Best match" : "Intel"}
                badgeCls={result.winner === "intel" ? "mob-score-best-match" : "mob-score-best-value"}
              />
            )}
            {result.amd && (
              <MobRecCard
                title="AMD Build"
                data={result.amd}
                badge={result.winner === "amd" ? "Best match" : "Best value"}
                badgeCls={result.winner === "amd" ? "mob-score-best-match" : "mob-score-best-value"}
                borderColor={result.winner !== "amd" ? "rgba(123,97,255,0.2)" : undefined}
              />
            )}
          </>
        ) : (
          !result?.error && (
            <div className="mob-no-results">
              <span>🤖</span>
              <p>Set your preferences above<br />and tap Generate Builds.</p>
            </div>
          )
        )}
      </div>
    </>
  );
}
