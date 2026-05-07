export default function BuildSummaryV2({ build, onPick, onRemove }) {
  const slots = ["cpu", "gpu", "mb", "ram", "storage"];

  return (
    <div className="build-summary-grid">
      {slots.map((slot) => {
        const part = build.parts[slot];

        return (
          <div key={slot} className="build-slot">
            {part ? (
              <>
                <div className="slot-image">
                  {part.image_url && <img src={part.image_url} alt={part.title} />}
                </div>

                <div className="slot-info">
                  <div className="slot-title">{part.title}</div>

                  <div className="slot-specs">
                    {Object.entries(part.specs || {}).map(([k, v]) => (
                      <div key={k} className="slot-spec">
                        <span className="spec-key">{k}</span>
                        <span className="spec-value">{v}</span>
                      </div>
                    ))}
                  </div>

                  <div className="slot-bottom">
                    <span className="slot-price">{part.best_price} ден</span>
                    <span className="slot-store">{part.store}</span>
                  </div>
                </div>

                <div className="slot-actions">
                  <button onClick={() => onPick(slot)}>Change</button>
                  <button className="danger" onClick={() => onRemove(slot)}>
                    Remove
                  </button>
                </div>
              </>
            ) : (
              <div className="empty-slot">
                <div className="empty-title">{slot.toUpperCase()}</div>
                <button onClick={() => onPick(slot)}>Select {slot}</button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
