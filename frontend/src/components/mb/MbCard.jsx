export default function MbCard({ mb, onAdd, onDetails }) {
  return (
    <div className="pc-card">
      <div
        className="pc-card-click"
        onClick={() => onDetails(mb.product_id)}
      >
        <div className="pc-card-image">
          <img src={mb.image_url} alt={mb.mb_model} referrerPolicy="no-referrer" onError={(e) => (e.target.style.display = "none")} />
        </div>

        <div className="pc-card-title">{mb.mb_model}</div>

        <div className="pc-card-price">
          from <b>{mb.min_price} MKD</b>
        </div>

        <div className="pc-card-specs">
          <div>Socket: {mb.socket}</div>
          <div>{mb.memory_type}</div>
          <div>{mb.form_factor}</div>
        </div>
      </div>

      <button
        className="pc-card-action"
        onClick={(e) => {
          e.stopPropagation();
          onAdd(mb.product_id);
        }}
      >
        + Add to build
      </button>
    </div>
  );
}
