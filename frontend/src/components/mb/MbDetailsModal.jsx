import { useEffect, useState, useRef } from "react";
import { fetchMbDetails } from "../../api/mbProducts";

export default function MbDetailsModal({ productId, onClose, onAdd }) {
  const [data, setData] = useState(null);
  const modalRef = useRef(null);

  useEffect(() => {
    if (!productId) return;
    fetchMbDetails(productId).then(setData);
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
                  src={data.offers[0]?.image_url}
                  alt={data.specs.model}
                  onError={(e) => (e.target.style.display = "none")}
                />
              </div>

              <div className="details-specs">
                <h3 className="section-title">Specifications</h3>

                <table className="spec-table">
                  <tbody>
                    <tr><td>Socket</td><td>{data.specs.socket}</td></tr>
                    <tr><td>Memory Type</td><td>{data.specs.memory_type}</td></tr>
                    <tr><td>Form Factor</td><td>{data.specs.form_factor}</td></tr>
                    <tr><td>Max RAM</td><td>{data.specs.max_ram_mhz} MHz</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* RIGHT */}
            <div className="details-right">
              <div className="details-title">
                <div className="badge">Motherboard</div>
                <h2>{data.specs.model}</h2>
                <div className="price">{data.offers[0]?.price} MKD</div>
              </div>

              <div className="details-actions">
                <button className="primary" onClick={() => onAdd?.(productId)}>
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
