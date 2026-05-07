export default function StorageCard({ storage, onDetails, onAdd }) {
  return (
    <div className="pc-card">
      <div
        className="pc-card-click"
        onClick={() => onDetails(storage.product_id)}
      >
        <div className="pc-card-image">
          <img
            src={storage.image_url}
            alt="Storage"
            onError={(e) => (e.target.style.display = "none")}
          />
        </div>

        <div className="pc-card-title">
          {storage.brand} {storage.series}
        </div>

        <div className="pc-card-price">
          from <b>{storage.min_price} MKD</b>
        </div>

        <div className="pc-card-specs">
          <div>{storage.capacity_gb} GB</div>
          <div>{storage.type}</div>
          <div>{storage.interface}</div>
        </div>
      </div>

      <button
        className="pc-card-action"
        onClick={(e) => {
          e.stopPropagation();
          onAdd(storage.product_id);
        }}
      >
        + Add to build
      </button>
    </div>
  );
}
