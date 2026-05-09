import { useState } from "react";
import CpuPicker from "../cpu/CpuPicker";
import GpuPicker from "../gpu/GpuPicker";
import RamPicker from "../ram/RamPicker";
import MbPicker from "../mb/MbPicker";
import StoragePicker from "../storage/StoragePicker";
import ComparePickerModal from "./ComparePickerModal";

const PICKERS = {
  cpu: CpuPicker,
  gpu: GpuPicker,
  ram: RamPicker,
  mb: MbPicker,
  storage: StoragePicker,
};

export default function CompareSlot({ category, item, onPick, onRemove }) {
  const [open, setOpen] = useState(false);
  const Picker = PICKERS[category];

  // EMPTY SLOT
  if (!item) {
    return (
      <div className="compare-slot empty">
        <button onClick={() => setOpen(true)}>
          Select {category.toUpperCase()}
        </button>

        {open && (
          <ComparePickerModal
            title={`Select ${category.toUpperCase()}`}
            onClose={() => setOpen(false)}
          >
            <Picker
              onSelect={(id) => {
                onPick(id);
                setOpen(false);
              }}
            />
          </ComparePickerModal>
        )}
      </div>
    );
  }

  // FILLED SLOT
  // CompareSlot.jsx (FILLED SLOT)
return (
  <div className="compare-slot filled card">
    <button className="remove" onClick={onRemove}>✕</button>

    {item.image_url && (
      <img
        src={item.image_url}
        alt={item.model}
        className="compare-card-image"
        referrerPolicy="no-referrer"
        onError={(e) => (e.target.style.display = "none")}
      />
    )}

    <div className="compare-card-model">
      {item.model}
    </div>

    {item.specs && (
      <table className="compare-card-specs">
        <tbody>
          {Object.entries(item.specs).map(([k, v]) => (
            <tr key={k}>
              <td>{k}</td>
              <td>{v ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

}
