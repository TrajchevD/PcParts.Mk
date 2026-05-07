import { useEffect, useState, useRef } from "react";
import { fetchCpuDetails } from "../../api/cpuProducts";

export default function CpuDetailsModal({ cpuModel, onClose, onAdd }) {
  const [data, setData] = useState(null);
  const modalRef = useRef(null);

  useEffect(() => {
    if (!cpuModel) return;
    fetchCpuDetails(cpuModel).then(setData);
  }, [cpuModel]);

  // ✅ close when clicking outside
  function handleBackdropClick(e) {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  }
  function getStoreLogo(storeName) {
  return `/logos/${storeName.toLowerCase()}.png`;
}


  if (!cpuModel) return null;

  return (
    <div className="modal-backdrop" onMouseDown={handleBackdropClick}>
      <div
        className="modal-card modal-wide"
        ref={modalRef}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>✕</button>

        {!data && <div className="muted">Loading...</div>}

        {data && (
  <div className="details-layout">
  {/* LEFT SIDE (2/3) */}
  <div className="details-left">
    <div className="details-image">
      <img
        src={data.offers[0]?.image_url}
        alt={data.cpu_model}
      />
    </div>

    <div className="details-specs">
      <h3 className="section-title">Specifications</h3>

      <table className="spec-table">
        <tbody>
          <tr><td>Brand</td><td>{data.specs.brand}</td></tr>
          <tr><td>Socket</td><td>{data.specs.socket}</td></tr>
          <tr><td>Cores</td><td>{data.specs.cores}</td></tr>
          <tr><td>Threads</td><td>{data.specs.threads}</td></tr>
          <tr><td>Base Clock</td><td>{data.specs.base_clock_ghz} GHz</td></tr>
          <tr><td>Boost Clock</td><td>{data.specs.boost_clock_ghz} GHz</td></tr>
          <tr><td>TDP</td><td>{data.specs.tdp_w} W</td></tr>
          <tr><td>Memory</td><td>{data.specs.memory_type}</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  {/* RIGHT SIDE (1/3) */}
  <div className="details-right">
    <div className="details-title">
      <div className="badge">CPU</div>
      <h2>{data.cpu_model}</h2>
      <div className="price">{data.offers[0]?.price} MKD</div>
    </div>

    <div className="details-actions">
      <button
          className="primary"
          onClick={() => onAdd(cpuModel)}
        >
          + Add to build
        </button>
      <button className="btn-secondary">Compare</button>
    </div>

    <div className="details-offers">
      <h3 className="section-title">Available Offers</h3>

      <div className="offers-list">
        {data.offers.map(o => (
          <div key={o.offer_id} className="offer-row">
            <img
              src={`/logos/${o.store_name.toLowerCase()}.png`}
              className="store-logo"
              alt={o.store_name}
              onError={(e) => (e.target.style.display = "none")}
            />

            <div>
              <div className="offer-store">{o.store_name}</div>
              <div className={o.in_stock ? "in-stock" : "out-stock"}>
                {o.in_stock ? "In stock" : "Out of stock"}
              </div>
            </div>

            <div className="offer-right">
              <div className="offer-price">{o.price} MKD</div>
              <a
                href={o.product_url}
                target="_blank"
                rel="noreferrer"
                className="btn-buy"
              >
                Buy
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
</div>

)}

      </div>
    </div>
  );
}
