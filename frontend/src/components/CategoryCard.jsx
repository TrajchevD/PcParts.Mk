import { Link } from "react-router-dom";

const LABELS = {
  cpu: "CPU",
  gpu: "GPU",
  ram: "RAM",
  memory: "Storage",
  mb: "Motherboards",
};

export default function CategoryCard({ category, count }) {
  return (
    <Link to={`/category/${category}`} className="card">
      <h3 className="cardTitle">{LABELS[category] || category}</h3>
      <div className="muted">{count} products in stock</div>
    </Link>
  );
}
