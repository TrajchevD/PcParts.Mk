export default function PartsModalV2({ title, onClose, children }) {
  return (
    <div className="modal-overlay">
      <div
        className="modal"
        style={{
          width: "90%",
          maxWidth: 1200,
          maxHeight: "90vh",          // ✅ limit modal height
          display: "flex",
          flexDirection: "column",    // ✅ stack header + body
        }}
      >
        {/* HEADER (fixed) */}
        <div className="modal-header">
          <h3>{title}</h3>
          <button onClick={onClose}>✕</button>
        </div>

        {/* BODY (scrollable) */}
        <div
          className="modal-body"
          style={{
            flex: 1,
            overflowY: "auto",        // ✅ scrolling happens here
            paddingRight: 6,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
