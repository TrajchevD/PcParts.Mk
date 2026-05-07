import PartCard from "./PartCard";

export default function PartsGrid({ options, slot, onSelect }) {
  if (!options.length) {
    return <div>No options found.</div>;
  }

  return (
    <div className="parts-list">
      {options.map((p) => (
        <PartCard
          key={p.product_id}
          part={p}
          slot={slot}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
