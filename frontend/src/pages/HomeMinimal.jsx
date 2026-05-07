import { useNavigate } from "react-router-dom";

export default function HomeMinimal() {
    const navigate = useNavigate();

    const categories = [
        { title: "All-AMD Red Build", icon: "🔴", desc: "High performance budget gaming", path: "/category/amd" },
        { title: "Baller White 4K RGB", icon: "⚪", desc: "Premium white aesthetics", path: "/category/white" },
        { title: "Modern 1440p Gaming", icon: "🔵", desc: "The sweet spot for gamers", path: "/category/1440p" },
        { title: "Creator Workstation", icon: "🎨", desc: "High core count & RAM", path: "/category/workstation" },
    ];

    return (
        <div className="home-container" style={{ paddingTop: '40px' }}>
            <div className="section-header" style={{ marginTop: '0' }}>
                <h2 className="section-title">Select a Category</h2>
            </div>

            <div className="category-grid">
                {categories.map((cat, index) => (
                    <div
                        key={index}
                        className="card"
                        onClick={() => navigate(cat.path)}
                    >
                        <div className="card-icon" style={{ fontSize: '2rem' }}>
                            {cat.icon}
                        </div>
                        <div className="card-title">{cat.title}</div>
                        <div className="card-desc">{cat.desc}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
