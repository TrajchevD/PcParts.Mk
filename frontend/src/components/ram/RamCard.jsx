export default function RamCard({ ram, onDetails, onAdd }) {
  return (
    <div className="pc-card">
      {/* CLICK → DETAILS */}
      <div
        className="pc-card-click"
        onClick={() => onDetails(ram.product_id)}
      >
        <div className="pc-card-image">
          <img
            src={ram.image_url}
            alt="RAM"
            referrerPolicy="no-referrer"
            onError={(e) => (e.target.style.display = "none")}
          />
        </div>

        <div className="pc-card-title">
          {ram.brand} {ram.series}
        </div>

        <div className="pc-card-price">
          from <b>{ram.min_price} MKD</b>
        </div>

        <div className="pc-card-specs">
          <div>{ram.total_capacity_gb} GB</div>
          <div>{ram.speed_mhz} MHz</div>
          <div>{ram.memory_type}</div>
        </div>
      </div>

      {/* ADD */}
      <button
        className="pc-card-action"
        onClick={(e) => {
          e.stopPropagation();
          onAdd(ram.product_id);
        }}
      >
        + Add to build
      </button>
    </div>
  );
}
