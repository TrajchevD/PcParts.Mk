export default function GpuCard({ gpu, onAdd, onDetails }) {
  return (
    <div className="pc-card">
      {/* CARD CLICK → DETAILS */}
      <div
        className="pc-card-click"
        onClick={() => onDetails(gpu.gpu_model)}
      >
        <div className="pc-card-image">
          <img src={gpu.image_url} alt={gpu.gpu_model} referrerPolicy="no-referrer" onError={(e) => (e.target.style.display = "none")} />
        </div>

        <div className="pc-card-title">{gpu.gpu_model}</div>

        <div className="pc-card-price">
          from <b>{gpu.min_price} MKD</b>
        </div>

        <div className="pc-card-specs">
          <div>{gpu.vram_gb} GB VRAM</div>
          <div>{gpu.offer_count} offers</div>
        </div>
      </div>

      {/* BUTTON → ADD TO BUILD */}
      <button
        className="pc-card-action"
        onClick={(e) => {
          e.stopPropagation();
          onAdd(gpu);
        }}
      >
        + Add to build
      </button>
    </div>
  );
}

