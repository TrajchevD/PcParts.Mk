"""Quick sanity check for normalizer.py — run with: python test_normalizer.py"""
from normalizer import extract_model_key

cases = [
    # CPU — Cyrillic / mixed titles
    ("cpu", "Процесор AMD Ryzen 7 9800X3D"),
    ("cpu", "Процесор АМД Рајзен 7 7800X3D, 4.2GHz"),
    ("cpu", "Процесор Интел Кор Ултра 7 265KF"),
    ("cpu", "Процесор Интел Кор i7-14700F"),
    ("cpu", "AMD Ryzen 7 9800X3D 4,7 GHz 96MB L3 Tray процесор"),
    ("cpu", "Десктоп процесор AMD Ryzen 7 7800X3D, 8 јадра 16 нишки, 4.2 GHz"),
    ("cpu", "[OUTLET] Procesor AMD Ryzen 5 7600X"),
    ("cpu", "Procesor Intel i9-14900KF"),
    # CPU
    ("cpu", "Intel Core i5-13600K Box"),
    ("cpu", "Procesor AMD Ryzen 5 7600X"),
    ("cpu", "AMD Ryzen 9 7950X3D"),
    ("cpu", "Intel Core Ultra 9 285K"),
    ("cpu", "AMD Ryzen Threadripper PRO 5965WX"),

    # GPU
    ("gpu", "MSI GeForce RTX 4070 Ti SUPER 16G GAMING X SLIM"),
    ("gpu", "ASUS TUF Gaming GeForce RTX 4090 OC"),
    ("gpu", "Sapphire Radeon RX 7900 XTX 24GB"),
    ("gpu", "Gigabyte GeForce RTX 4060 Ti SUPER"),
    ("gpu", "Intel Arc A770 16GB"),

    # RAM
    ("ram", "RAM DIMM Kingston 16GB DDR5 5600MHz Fury Beast CL40"),
    ("ram", "Corsair Vengeance 32GB (2x16GB) DDR5 6000MHz CL36"),
    ("ram", "Kingston Fury Beast 16GB DDR4 3600MHz"),
    ("ram", "G.Skill Trident Z5 64GB Kit (2x32GB) DDR5-6400"),

    # MB
    ("mb", "ASUS ROG Strix B650E-F Gaming WiFi"),
    ("mb", "MSI MAG B550 Tomahawk MAX WiFi"),
    ("mb", "Gigabyte B650E Aorus Elite AX"),
    ("mb", "ASRock Z790 Taichi Carrara DDR5"),
    ("mb", "ASUS TUF Gaming X670E-Plus WiFi"),

    # Storage — Latin titles
    ("storage", "Samsung 870 EVO 1TB 2.5\" SATA III"),
    ("storage", "WD Red SA500, 500GB, 2.5\" SATA III"),
    ("storage", "Seagate BarraCuda 4TB 3.5\" SATA III"),
    ("storage", "SSD диск WD Black 850X, 1TB, M.2 NVMe"),
    ("storage", "Silicon Power S56, 240GB, 2.5\" SATA III"),
    ("storage", "SSD XPG GAMMIX S70 Blade, 1TB, M.2 NVMe PCIe 4.0"),
    ("storage", "Goodram PX700, 1TB, M.2 PCIe Gen4"),
    ("storage", "Apacer AS350X, 256GB, 2.5\" SATA III"),

    # Storage — Macedonian/Cyrillic prefixes
    ("storage", "Внатрешен SSD Adata Legend 860, 500GB, M.2 PCIe 4.0"),
    ("storage", "Надворешен SSD ADATA SC610, 2TB, USB 3.2, црн"),
    ("storage", "SSD диск Silicon Power A55, 256GB, M.2 2280 SATA"),
    ("storage", "HDD диск Seagate BarraCuda, 4TB, 3.5\" SATA III"),
    ("storage", "Диск SSD Самсунг 870 ЕВО, 2.5\", 2TB, САТА"),

    # Storage — Albanian prefixes
    ("storage", "Disk i jashtëm HDD WD Elements SE 5TB, i zi"),
    ("storage", "Hard disk i jashtëm HDD Seagate Expansion Portable 4TB"),
    ("storage", "Disk i jashtëm HDD WD My Book 18000 GB, i zi"),
]

print(f"{'Category':<10} {'Key':<40} {'Title'}")
print("-" * 110)
for cat, title in cases:
    key = extract_model_key(title, cat)
    status = "✓" if key else "✗"
    print(f"{status} {cat:<9} {str(key):<40} {title[:60]}")
