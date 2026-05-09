import { useOutletContext } from "react-router-dom";

export default function MobileNavBar({ title }) {
  const { toggleSidebar } = useOutletContext() || {};
  return (
    <div className="mob-topbar mob-only">
      <span className="mob-page-title">{title}</span>
      <button className="mob-icon-btn" onClick={toggleSidebar} aria-label="Open menu">☰</button>
    </div>
  );
}
