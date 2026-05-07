const SLOT_LABELS = {
  cpu: "CPU",
  gpu: "GPU",
  ram: "RAM",
  mb: "Motherboard",
  storage: "Storage",
  recommended_psu_w: "Recommended PSU",
};

function getModelName(value) {
  if (!value) return "—";
  return value.model || value.cpu_model || value.gpu_model || value.mb_model || value.series || JSON.stringify(value);
}

export default function RecommendationBuildView({ title, data, highlight }) {
  if (!data) return null;

  const { build, total_price, value_score } = data;

  return (
    <div className={`recommend-card ${highlight ? "winner" : ""}`}>
      <h3>
        {highlight && <span style={{ color: "var(--neon-green)", marginRight: 6 }}>🏆</span>}
        {title}
      </h3>

      <div className="recommend-meta">
        Total: <b>{total_price?.toLocaleString() ?? "—"} MKD</b>
        &nbsp;·&nbsp;Value score: <b>{value_score ?? "—"}</b>
      </div>

      {Object.entries(build).map(([key, value]) => {
        if (!value) return null;

        if (key === "recommended_psu_w") {
          return (
            <div key={key} className="recommend-part">
              <div className="recommend-part-name">{SLOT_LABELS[key] ?? key.toUpperCase()}</div>
              <div className="recommend-part-model">{value}W</div>
            </div>
          );
        }

        return (
          <div key={key} className="recommend-part">
            <div className="recommend-part-name">{SLOT_LABELS[key] ?? key.toUpperCase()}</div>
            <div className="recommend-part-model">{getModelName(value)}</div>
            {value.min_price != null && (
              <div className="recommend-part-price">{value.min_price?.toLocaleString()} MKD</div>
            )}
            {(value.sticks != null && value.sticks > 1) && (
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>×{value.sticks}</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
