import { useState } from "react";
import ComparePickerModal from "./ComparePickerModal";
import CpuPicker from "../cpu/CpuPicker";
import GpuPicker from "../gpu/GpuPicker";
import RamPicker from "../ram/RamPicker";
import MbPicker from "../mb/MbPicker";
import StoragePicker from "../storage/StoragePicker";

const PICKERS = {
  cpu: CpuPicker,
  gpu: GpuPicker,
  ram: RamPicker,
  mb: MbPicker,
  storage: StoragePicker,
};

export default function CompareTable({ category, items = [], onAdd, onRemove }) {
  const [open, setOpen] = useState(false);
  const Picker = PICKERS[category];

  const specKeys = items.length ? Object.keys(items[0].specs) : [];

  return (
    <>
      <table className="compare-table">
        <thead>
          <tr>
            <th>Spec</th>

            {items.map(item => (
              <th key={item.id}>
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt={item.model}
                    className="compare-header-img"
                    referrerPolicy="no-referrer"
                    onError={(e) => (e.target.style.display = "none")}
                  />
                )}
                <div className="compare-header-model">
                  {item.model}
                </div>
                <button
                  className="compare-remove"
                  onClick={() => onRemove(item.id)}
                >
                  Remove
                </button>
              </th>
            ))}

            {/* ADD COLUMN */}
            <th className="compare-add-column">
              <button
                className="compare-add-btn"
                onClick={() => setOpen(true)}
              >
                + Add {category.toUpperCase()}
              </button>
            </th>
          </tr>
        </thead>

        <tbody>
          {specKeys.map(key => (
            <tr key={key}>
              <td className="spec-label">
                {key.replace(/_/g, " ").toUpperCase()}
              </td>

              {items.map(item => (
                <td key={item.id}>
                  {item.specs[key] ?? "—"}
                </td>
              ))}

              <td></td>
            </tr>
          ))}
        </tbody>
      </table>

      {open && (
        <ComparePickerModal
          title={`Select ${category}`}
          onClose={() => setOpen(false)}
        >
          <Picker
            onSelect={(id) => {
              onAdd(id);
              setOpen(false);
            }}
          />
        </ComparePickerModal>
      )}
    </>
  );
}