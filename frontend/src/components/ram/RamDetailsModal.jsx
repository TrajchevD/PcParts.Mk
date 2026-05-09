import { useEffect, useRef, useState } from "react";
import { fetchRamDetails } from "../../api/ramProducts";

export default function RamDetailsModal({ productId, onClose, onAdd }) {
  const [data, setData] = useState(null);
  const modalRef = useRef(null);

  useEffect(() => {
    if (!productId) return;
    fetchRamDetails(productId).then(setData);
  }, [productId]);

  function handleBackdropClick(e) {
    if (modalRef.current && !modalRef.current.contains(e.target)) {
      onClose();
    }
  }

  if (!productId) return null;

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
            {/* LEFT */}
            <div className="details-left">
              <div className="details-image">
                <img
                  src={data.offers.find(o => o.image_url)?.image_url}
                  alt="RAM"
                  referrerPolicy="no-referrer"
                  onError={(e) => (e.target.style.display = "none")}
                />
              </div>

              <div className="details-specs">
                <h3 className="section-title">Specifications</h3>

                <table className="spec-table">
                  <tbody>
                    <tr><td>Memory type</td><td>{data.specs.memory_type}</td></tr>
                    <tr><td>Total capacity</td><td>{data.specs.total_capacity_gb} GB</td></tr>
                    <tr><td>Modules</td><td>{data.specs.kit_modules}</td></tr>
                    <tr><td>Speed</td><td>{data.specs.speed_mhz} MHz</td></tr>
                    <tr><td>CAS latency</td><td>CL{data.specs.cas_latency}</td></tr>
                    <tr><td>Form factor</td><td>{data.specs.form_factor}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* RIGHT */}
            <div className="details-right">
              <div className="details-title">
                <div className="badge">RAM</div>
                <h2>
                  {data.specs.model}
                </h2>
                <div className="price">
                  {data.offers[0]?.price} MKD
                </div>
              </div>

              <div className="details-actions">
                <button
                  className="primary"
                  onClick={() => onAdd(productId)}
                >
                  + Add to build
                </button>
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
