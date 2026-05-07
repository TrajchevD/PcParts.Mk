export default function ComparePickerModal({ title, onClose, children }) {
  return (
    <div className="compare-modal-backdrop">
      <div className="compare-modal">
        <div className="compare-modal-header">
          <h3>{title}</h3>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="compare-modal-body">
          {children}
        </div>
      </div>
    </div>
  );
}
