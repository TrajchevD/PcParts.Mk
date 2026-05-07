export default function CpuCard({ cpu, onAdd, onDetails }) {
  return (
    <div className="pc-card">
      <div className="pc-card-click" onClick={() => onDetails(cpu.cpu_model)}>
        <div className="pc-card-image">
          <img src={cpu.image_url} alt={cpu.cpu_model} />
        </div>
        <div className="pc-card-title">{cpu.cpu_model}</div>
        <div className="pc-card-price">from <b>{cpu.min_price} MKD</b></div>
        <div className="pc-card-specs">
          <div>Socket: {cpu.socket}</div>
          <div>{cpu.cores} cores</div>
          <div>{cpu.offer_count} offers</div>
        </div>
      </div>
      <button className="pc-card-action" onClick={e => { e.stopPropagation(); onAdd(cpu); }}>
        + Add to build
      </button>
    </div>
  );
}
