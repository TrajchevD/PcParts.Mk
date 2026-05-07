export default function BuildSummary({ build, onPick, onRemove }) {
  if (!build) return null;

  const HIDDEN_KEYS = ["id", "image", "title"];

  const ALL_SLOTS = ["cpu", "mb", "ram", "gpu", "storage"];

  const normalizedParts = ALL_SLOTS.reduce((acc, slot) => {
    acc[slot] = build.parts?.[slot] ?? null;
    return acc;
  }, {});
  
  const formatKey = (key) =>
    key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Selected parts</h3>

      {Object.entries(normalizedParts).map(([slot, part]) => (

        <div
          key={slot}
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 12,
            marginBottom: 14,
          }}
        >
          <h4 style={{ marginBottom: 8 }}>{slot.toUpperCase()}</h4>

          {part ? (
            <>
              {/* Header */}
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <img
                  src={part.image}
                  alt={part.title}
                  style={{ width: 60, height: 60, objectFit: "contain" }}
                />
                <strong>{part.model ?? part.title}</strong>
              </div>

              {/* ACTION BUTTONS */}
              <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
                <button onClick={() => onPick(slot)}>
                  Swap
                </button>
                    
                <button
                  onClick={() => onRemove(slot)}
                  style={{ color: "red" }}
                >
                  ✕ Remove
                </button>
              </div>
            
            <div style={{ marginTop: 10 }}>
                {Object.entries(part)
                  .filter(([key]) => !HIDDEN_KEYS.includes(key))
                  .map(([key, value]) => (
                    <div
                      key={key}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: 14,
                        marginBottom: 4,
                      }}
                    >
                      <span style={{ opacity: 0.7 }}>{formatKey(key)}</span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
              </div>
          </>
          ) : (
            <button onClick={() => onPick(slot)}>
              + Pick {slot.toUpperCase()}
            </button>
          )}
              {/* Specs
              
          ) : (
            <span>—</span> */}
          {/* )} */}
        </div>
      ))}
    </div>
  );
}
