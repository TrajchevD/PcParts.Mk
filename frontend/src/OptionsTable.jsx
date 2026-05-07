export function OptionsTable({ options, onSelect }) {
  if (!options.length) {
    return <div>No compatible parts found.</div>;
  }

  return (
    <table className="options">
      <thead>
        <tr>
          <th>Name</th>
          <th>Specs</th>
          <th>Price</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {options.map((p) => (
          <tr key={p.product_id}>
            <td>{p.canonical_title || p.title}</td>
            <td>
              {p.socket && <>Socket: {p.socket}<br /></>}
              {p.memory_type && <>RAM: {p.memory_type}<br /></>}
              {p.vram_gb && <>VRAM: {p.vram_gb}GB</>}
            </td>
            <td>{p.min_price ?? "—"} ден.</td>
            <td>
              <button onClick={() => onSelect(p.product_id)}>
                Select
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
