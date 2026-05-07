// function renderPrimarySpec(part, slot) {
//   switch (slot) {
//     case "cpu":
//       return (
//         <>
//           {part.socket && <span>Socket {part.socket}</span>}
//           {part.model && <span> · {part.model}</span>}
//         </>
//       );

//     case "mb":
//       return (
//         <>
//           {part.socket && <span>scazsczs{part.socket}</span>}
//           {part.memory_type && (
//             <span>
//               {part.memory_type}
//               {part.memory_slots ? ` × ${part.memory_slots}` : ""}
//             </span>
//           )}
//           {part.form_factor && <span>{part.form_factor}</span>}
//         </>
//       );


//     case "gpu":
//       return (
//         <>
//           {part.vram_gb && <span>{part.vram_gb} GB</span>}
//           {part.gpu_model && <span> · {part.gpu_model}</span>}
//         </>
//       );

//     case "ram":
//       return (
//         <>
//           {part.total_capacity_gb && <span>{part.total_capacity_gb} GB</span>}
//           {part.speed_mhz && <span> · {part.speed_mhz} MHz</span>}
//         </>
//       );

//     case "storage":
//       return (
//         <>
//           {part.storage_type && <span>{part.storage_type}</span>}
//           {part.capacity_gb && <span> · {part.capacity_gb} GB</span>}
//         </>
//       );

//     default:
//       return null;
//   }
// }

function getPrimarySpec(part, slot) {
  switch (slot) {
    case "cpu":
      return part.socket ? `Socket: ${part.socket}` : null;

    case "mb":
      return (
        <>
          {part.socket && <span>Socket: {part.socket}</span>}
          {part.memory_type && (
            <span>
              {" · DDR: "}
              {part.memory_type}
              {part.memory_slots ? ` × ${part.memory_slots}` : ""}
            </span>
          )}
          {part.form_factor && <span>{" · "}{part.form_factor}</span>}
        </>
      );

    case "gpu":
      return (
        <>
          {part.vram_gb && <span>{part.vram_gb} GB</span>}
          {part.gpu_model && <span>{" · "}{part.gpu_model}</span>}
        </>
      );

    case "ram":
      return (
        <>
          {part.total_capacity_gb && (
            <span>{part.total_capacity_gb} GB</span>
          )}
          {part.speed_mhz && (
            <span>{" · "}{part.speed_mhz} MHz</span>
          )}
        </>
      );

    case "storage":
      return (
        <>
          {part.storage_type && <span>{part.storage_type}</span>}
          {part.capacity_gb && <span>{" · "}{part.capacity_gb} GB</span>}
        </>
      );

    default:
      return null;
  }
}






export default function PartCard({ part, slot, onSelect }) {
  const primarySpec = getPrimarySpec(part, slot);

  return (
    <div className="part-row">
      {/* IMAGE */}
      <div className="part-image">
        <img
          src={part.image_url}
          alt={part.title}
          referrerPolicy="no-referrer"
          onError={(e) => {
            e.currentTarget.src =
              "https://via.placeholder.com/80x80?text=No+Image";
          }}
        />
      </div>

      {/* INFO */}
      <div className="part-info">
        <div className="part-title">{part.title}</div>

        <div className="part-price">
          {part.min_price ? `${part.min_price} ден.` : "—"}
        </div>

        {primarySpec && (
          <div className="part-specs">{primarySpec}</div>
        )}
      </div>

      {/* ACTION */}
      <div className="part-action">
        <button type="button" onClick={() => onSelect(part.product_id)}>
          Select
        </button>
      </div>
    </div>
  );
}


