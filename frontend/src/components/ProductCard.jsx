import { useState } from "react";
import { getStoreLogo } from "./storeLogos";

function formatPriceText(priceText, priceNumber) {
  if (priceText && String(priceText).trim().length > 0) return priceText;
  if (priceNumber != null) return `${priceNumber} ден.`;
  return "";
}

export default function ProductCard({ p }) {
  const storeLogo = getStoreLogo(p.store);
  const [imgError, setImgError] = useState(false);

  return (
    <a className="card" href={p.link} target="_blank" rel="noreferrer">
      {/* IMAGE AREA */}
      {!imgError && p.image ? (
        <img
          className="productImg"
          src={p.image}
          alt={p.title}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setImgError(true)}
        />
      ) : (
        <div className="productImg placeholder">
          <img
            src={storeLogo}
            alt={p.store}
            style={{
              width: 80,
              height: 80,
              objectFit: "contain",
              opacity: 0.85,
            }}
          />
        </div>
      )}

      {/* INFO */}
      <div style={{ marginTop: 10 }}>
        <div style={{ fontWeight: 700, lineHeight: 1.25 }}>
          {p.title}
        </div>

        <div className="row" style={{ marginTop: 10 }}>
          <div className="price">
            {formatPriceText(p.price_text, p.price)}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <img className="storeLogo" src={storeLogo} alt={p.store} />
            <span className="muted" style={{ fontSize: 12 }}>
              {p.store}
            </span>
          </div>
        </div>
      </div>
    </a>
  );
}
