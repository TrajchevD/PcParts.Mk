import { Link } from "react-router-dom";

const PARTS = [
  { name: "Case", link: "/catalog/case", img: "/logos/case.png" },
  { name: "CPU", link: "/catalog/cpu", img: "/logos/cpu_v2.png" },
  { name: "Motherboard", link: "/catalog/mb", img: "/logos/mb_v2.png" },
  { name: "GPU", link: "/catalog/gpu", img: "/logos/gpu_v2.png" },
  { name: "RAM", link: "/catalog/ram", img: "/logos/ram_v2.png" },
  { name: "Storage", link: "/catalog/storage", img: "/logos/storage_v2.png" },
  { name: "Power Supply", link: "/catalog/psu", img: "/logos/psu_v2.png" },
  { name: "CPU Cooler", link: "/catalog/cooler", img: "/logos/cooler.png" },
];

const OTHERS = [
  // "Thermal Compound",
  // "Operating System",
  // "Sound Card",
  // "Network Card",
  // "VR Headset",
  // "Capture Card",
  // "Accessory",
];

export default function ProductFlyout({ visible, onClose }) {
  if (!visible) return null;

  return (
    <div className="product-flyout">
      <div className="flyout-grid">
        {PARTS.map((p) => (
          <Link
            to={p.link}
            key={p.name}
            className="flyout-item"
            onClick={onClose}
          >
            <div className="flyout-icon">
              <img src={p.img} alt={p.name} />
            </div>
            <span className="flyout-name">{p.name}</span>
          </Link>
        ))}
      </div>

      {/* <div className="flyout-list">
        {OTHERS.map((item) => (
          <Link
            to={`/catalog/other?q=${item}`}
            key={item}
            className="flyout-list-item"
            onClick={onClose}
          >
            {item}
          </Link>
        ))}
      </div> */}
    </div>
  );
}
