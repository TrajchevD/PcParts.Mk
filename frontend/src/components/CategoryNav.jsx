import { NavLink } from "react-router-dom";

const CATS = [
  { label: "CPUs",       path: "/catalog/cpu" },
  { label: "GPUs",       path: "/catalog/gpu" },
  { label: "Motherboards", path: "/catalog/mb" },
  { label: "RAM",        path: "/catalog/ram" },
  { label: "Storage",    path: "/catalog/storage" },
];

export default function CategoryNav() {
  return (
    <nav className="cat-nav">
      {CATS.map(c => (
        <NavLink
          key={c.path}
          to={c.path}
          className={({ isActive }) => `cat-nav-link${isActive ? " active" : ""}`}
        >
          {c.label}
        </NavLink>
      ))}
    </nav>
  );
}
