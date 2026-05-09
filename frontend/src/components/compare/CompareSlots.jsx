import CompareSlot from "./CompareSlot";

export default function CompareSlots({ category, slots = [], items = [], onChange }) {
  const MIN = 1;
  const MAX = 4;

  // Ensure we always have at least 2 visible slots
  const visibleSlots = slots.length ? slots : [null, null];

  function addSlot() {
    if (slots.length >= MAX) return;
    onChange([...slots, null]);
  }

  function updateSlot(index, productId) {
    const next = [...slots];
    next[index] = productId;
    onChange(next);
  }

  function removeSlot(index) {
    const next = [...slots];
    next.splice(index, 1);
    onChange(next);
  }

  function getItem(productId) {
    return items.find(i => String(i.id) === String(productId));
  }

  return (
    <div className="compare-slots">
      <div style={{ marginBottom: 12 }}>
        <button onClick={addSlot} disabled={slots.length >= MAX}>
          + Add product
        </button>
      </div>

      <div className="slot-grid">
        {visibleSlots.map((productId, index) => (
          <CompareSlot
            key={index}
            category={category}
            item={productId ? getItem(productId) : null}
            onPick={pid => updateSlot(index, pid)}
            onRemove={() => removeSlot(index)}
          />
        ))}
      </div>
    </div>
  );
}
