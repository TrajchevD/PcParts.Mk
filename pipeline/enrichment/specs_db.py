"""
Reference spec database for known CPU and GPU models.

Used as a fallback to fill NULL optional fields for products whose spec pages
didn't provide structured data (Setec title-only, Gjirafa50 Macedonian format, etc.).

Data sourced from manufacturer spec sheets. Keys are normalised model strings
(uppercase, no extra spaces) matched against the stored cpu_model / gpu_model.
"""

# ── CPU reference ─────────────────────────────────────────────────────────────
# Key: normalised model string fragment (matched with str.upper())
# Value: dict of fields — only non-None values will be written to DB
#
# Fields: cores, threads, base_clock_ghz, boost_clock_ghz, tdp_w, memory_type

CPU_SPECS: list[tuple[str, dict]] = [
    # ── Intel Core Ultra 200 (Arrow Lake, LGA1851) ───────────────────────────
    ("CORE ULTRA 9 285K",  dict(cores=24, threads=24, base_clock_ghz=3.7, boost_clock_ghz=5.7, tdp_w=125, memory_type="DDR5")),
    ("CORE ULTRA 9 285",   dict(cores=24, threads=24, base_clock_ghz=3.7, boost_clock_ghz=5.6, tdp_w=65,  memory_type="DDR5")),
    ("CORE ULTRA 7 265K",  dict(cores=20, threads=20, base_clock_ghz=3.9, boost_clock_ghz=5.5, tdp_w=125, memory_type="DDR5")),
    ("CORE ULTRA 7 265F",  dict(cores=20, threads=20, base_clock_ghz=3.9, boost_clock_ghz=5.3, tdp_w=65,  memory_type="DDR5")),
    ("CORE ULTRA 7 265",   dict(cores=20, threads=20, base_clock_ghz=3.7, boost_clock_ghz=5.3, tdp_w=65,  memory_type="DDR5")),
    ("CORE ULTRA 5 245K",  dict(cores=14, threads=14, base_clock_ghz=4.2, boost_clock_ghz=5.2, tdp_w=125, memory_type="DDR5")),
    ("CORE ULTRA 5 245KF", dict(cores=14, threads=14, base_clock_ghz=4.2, boost_clock_ghz=5.2, tdp_w=125, memory_type="DDR5")),
    ("CORE ULTRA 5 235",   dict(cores=14, threads=14, base_clock_ghz=3.8, boost_clock_ghz=5.0, tdp_w=65,  memory_type="DDR5")),
    ("CORE ULTRA 5 225",   dict(cores=10, threads=10, base_clock_ghz=3.3, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR5")),
    ("CORE ULTRA 5 225F",  dict(cores=10, threads=10, base_clock_ghz=3.3, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR5")),

    # ── Intel Core 14th Gen (Raptor Lake Refresh, LGA1700) ───────────────────
    ("I9-14900KS", dict(cores=24, threads=32, base_clock_ghz=3.2, boost_clock_ghz=6.2, tdp_w=150, memory_type="DDR5")),
    ("I9-14900K",  dict(cores=24, threads=32, base_clock_ghz=3.2, boost_clock_ghz=6.0, tdp_w=125, memory_type="DDR5")),
    ("I9-14900KF", dict(cores=24, threads=32, base_clock_ghz=3.2, boost_clock_ghz=6.0, tdp_w=125, memory_type="DDR5")),
    ("I9-14900F",  dict(cores=24, threads=32, base_clock_ghz=2.0, boost_clock_ghz=5.8, tdp_w=65,  memory_type="DDR5")),
    ("I9-14900",   dict(cores=24, threads=32, base_clock_ghz=2.0, boost_clock_ghz=5.8, tdp_w=65,  memory_type="DDR5")),
    ("I7-14700K",  dict(cores=20, threads=28, base_clock_ghz=3.4, boost_clock_ghz=5.6, tdp_w=125, memory_type="DDR5")),
    ("I7-14700KF", dict(cores=20, threads=28, base_clock_ghz=3.4, boost_clock_ghz=5.6, tdp_w=125, memory_type="DDR5")),
    ("I7-14700F",  dict(cores=20, threads=28, base_clock_ghz=2.1, boost_clock_ghz=5.4, tdp_w=65,  memory_type="DDR5")),
    ("I7-14700",   dict(cores=20, threads=28, base_clock_ghz=2.1, boost_clock_ghz=5.4, tdp_w=65,  memory_type="DDR5")),
    ("I5-14600K",  dict(cores=14, threads=20, base_clock_ghz=3.5, boost_clock_ghz=5.3, tdp_w=125, memory_type="DDR5")),
    ("I5-14600KF", dict(cores=14, threads=20, base_clock_ghz=3.5, boost_clock_ghz=5.3, tdp_w=125, memory_type="DDR5")),
    ("I5-14600",   dict(cores=14, threads=20, base_clock_ghz=2.7, boost_clock_ghz=5.2, tdp_w=65,  memory_type="DDR5")),
    ("I5-14500",   dict(cores=14, threads=20, base_clock_ghz=2.6, boost_clock_ghz=5.0, tdp_w=65,  memory_type="DDR5")),
    ("I5-14400F",  dict(cores=10, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.7, tdp_w=65,  memory_type="DDR5")),
    ("I5-14400",   dict(cores=10, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.7, tdp_w=65,  memory_type="DDR5")),
    ("I3-14100F",  dict(cores=4,  threads=8,  base_clock_ghz=3.5, boost_clock_ghz=4.7, tdp_w=58,  memory_type="DDR5")),
    ("I3-14100",   dict(cores=4,  threads=8,  base_clock_ghz=3.5, boost_clock_ghz=4.7, tdp_w=60,  memory_type="DDR5")),

    # ── Intel Core 13th Gen (Raptor Lake, LGA1700) ───────────────────────────
    ("I9-13900KS", dict(cores=24, threads=32, base_clock_ghz=3.2, boost_clock_ghz=6.0, tdp_w=150, memory_type="DDR5")),
    ("I9-13900K",  dict(cores=24, threads=32, base_clock_ghz=3.0, boost_clock_ghz=5.8, tdp_w=125, memory_type="DDR5")),
    ("I9-13900KF", dict(cores=24, threads=32, base_clock_ghz=3.0, boost_clock_ghz=5.8, tdp_w=125, memory_type="DDR5")),
    ("I9 13900KF", dict(cores=24, threads=32, base_clock_ghz=3.0, boost_clock_ghz=5.8, tdp_w=125, memory_type="DDR5")),
    ("I9 13900K",  dict(cores=24, threads=32, base_clock_ghz=3.0, boost_clock_ghz=5.8, tdp_w=125, memory_type="DDR5")),
    ("I7-13700K",  dict(cores=16, threads=24, base_clock_ghz=3.4, boost_clock_ghz=5.4, tdp_w=125, memory_type="DDR5")),
    ("I7-13700F",  dict(cores=16, threads=24, base_clock_ghz=2.1, boost_clock_ghz=5.2, tdp_w=65,  memory_type="DDR5")),
    ("I7-13700",   dict(cores=16, threads=24, base_clock_ghz=2.1, boost_clock_ghz=5.2, tdp_w=65,  memory_type="DDR5")),
    ("I5-13600K",  dict(cores=14, threads=20, base_clock_ghz=3.5, boost_clock_ghz=5.1, tdp_w=125, memory_type="DDR5")),
    ("I5-13600KF", dict(cores=14, threads=20, base_clock_ghz=3.5, boost_clock_ghz=5.1, tdp_w=125, memory_type="DDR5")),
    ("I5-13500",   dict(cores=14, threads=20, base_clock_ghz=2.5, boost_clock_ghz=4.8, tdp_w=65,  memory_type="DDR5")),
    ("I5-13400F",  dict(cores=10, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR5")),
    ("I5-13400",   dict(cores=10, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR5")),
    ("I3-13100F",  dict(cores=4,  threads=8,  base_clock_ghz=3.4, boost_clock_ghz=4.5, tdp_w=58,  memory_type="DDR5")),
    ("I3-13100",   dict(cores=4,  threads=8,  base_clock_ghz=3.4, boost_clock_ghz=4.5, tdp_w=60,  memory_type="DDR5")),

    # ── Intel Core 12th Gen (Alder Lake, LGA1700) ────────────────────────────
    ("I9-12900KS", dict(cores=16, threads=24, base_clock_ghz=3.4, boost_clock_ghz=5.2, tdp_w=150, memory_type="DDR5")),
    ("I9-12900K",  dict(cores=16, threads=24, base_clock_ghz=3.2, boost_clock_ghz=5.2, tdp_w=125, memory_type="DDR5")),
    ("I9-12900KF", dict(cores=16, threads=24, base_clock_ghz=3.2, boost_clock_ghz=5.2, tdp_w=125, memory_type="DDR5")),
    ("I9-12900",   dict(cores=16, threads=24, base_clock_ghz=2.4, boost_clock_ghz=5.1, tdp_w=65,  memory_type="DDR5")),
    ("I9 12900",   dict(cores=16, threads=24, base_clock_ghz=2.4, boost_clock_ghz=5.1, tdp_w=65,  memory_type="DDR5")),
    ("I7-12700K",  dict(cores=12, threads=20, base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=125, memory_type="DDR5")),
    ("I7-12700KF", dict(cores=12, threads=20, base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=125, memory_type="DDR5")),
    ("I7-12700F",  dict(cores=12, threads=20, base_clock_ghz=2.1, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR5")),
    ("I7-12700",   dict(cores=12, threads=20, base_clock_ghz=2.1, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR5")),
    ("I7 12700",   dict(cores=12, threads=20, base_clock_ghz=2.1, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR5")),
    ("I5-12600K",  dict(cores=10, threads=16, base_clock_ghz=3.7, boost_clock_ghz=4.9, tdp_w=125, memory_type="DDR5")),
    ("I5-12600KF", dict(cores=10, threads=16, base_clock_ghz=3.7, boost_clock_ghz=4.9, tdp_w=125, memory_type="DDR5")),
    ("I5-12600",   dict(cores=6,  threads=12, base_clock_ghz=3.3, boost_clock_ghz=4.8, tdp_w=65,  memory_type="DDR5")),
    ("I5-12500",   dict(cores=6,  threads=12, base_clock_ghz=3.0, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR5")),
    ("I5-12400F",  dict(cores=6,  threads=12, base_clock_ghz=2.5, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("I5-12400",   dict(cores=6,  threads=12, base_clock_ghz=2.5, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("I3-12100F",  dict(cores=4,  threads=8,  base_clock_ghz=3.3, boost_clock_ghz=4.3, tdp_w=58,  memory_type="DDR4")),
    ("I3-12100",   dict(cores=4,  threads=8,  base_clock_ghz=3.3, boost_clock_ghz=4.3, tdp_w=60,  memory_type="DDR4")),
    ("I3 12100F",  dict(cores=4,  threads=8,  base_clock_ghz=3.3, boost_clock_ghz=4.3, tdp_w=58,  memory_type="DDR4")),
    ("I3 12100",   dict(cores=4,  threads=8,  base_clock_ghz=3.3, boost_clock_ghz=4.3, tdp_w=60,  memory_type="DDR4")),

    # ── Intel Core 11th Gen (Rocket Lake, LGA1200) ───────────────────────────
    ("I9-11900K",  dict(cores=8, threads=16, base_clock_ghz=3.5, boost_clock_ghz=5.2, tdp_w=125, memory_type="DDR4")),
    ("I7-11700K",  dict(cores=8, threads=16, base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=125, memory_type="DDR4")),
    ("I7-11700",   dict(cores=8, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR4")),
    ("I7 11700",   dict(cores=8, threads=16, base_clock_ghz=2.5, boost_clock_ghz=4.9, tdp_w=65,  memory_type="DDR4")),
    ("I5-11400F",  dict(cores=6, threads=12, base_clock_ghz=2.6, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("I3-10100F",  dict(cores=4, threads=8,  base_clock_ghz=3.6, boost_clock_ghz=4.3, tdp_w=65,  memory_type="DDR4")),
    ("I3 10100F",  dict(cores=4, threads=8,  base_clock_ghz=3.6, boost_clock_ghz=4.3, tdp_w=65,  memory_type="DDR4")),

    # ── Intel Core 10th Gen (Comet Lake, LGA1200) ────────────────────────────
    ("I5-10400F",  dict(cores=6, threads=12, base_clock_ghz=2.9, boost_clock_ghz=4.3, tdp_w=65, memory_type="DDR4")),
    ("I5-10400",   dict(cores=6, threads=12, base_clock_ghz=2.9, boost_clock_ghz=4.3, tdp_w=65, memory_type="DDR4")),
    ("I3-10100",   dict(cores=4, threads=8,  base_clock_ghz=3.6, boost_clock_ghz=4.3, tdp_w=65, memory_type="DDR4")),

    # ── Intel 9th Gen (LGA1151) ───────────────────────────────────────────────
    ("I5-9500F",   dict(cores=6, threads=6, base_clock_ghz=3.0, boost_clock_ghz=4.4, tdp_w=65, memory_type="DDR4")),
    ("I9-9900K",   dict(cores=8, threads=16, base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=95, memory_type="DDR4")),

    # ── Intel Pentium / Celeron (LGA1200) ─────────────────────────────────────
    ("PENTIUM G6405",  dict(cores=2, threads=4, base_clock_ghz=4.1, tdp_w=58, memory_type="DDR4")),
    ("CELERON G5905",  dict(cores=2, threads=2, base_clock_ghz=3.5, tdp_w=58, memory_type="DDR4")),
    ("G6405",          dict(cores=2, threads=4, base_clock_ghz=4.1, tdp_w=58, memory_type="DDR4")),
    ("G5905",          dict(cores=2, threads=2, base_clock_ghz=3.5, tdp_w=58, memory_type="DDR4")),
    ("G3260",          dict(cores=2, threads=2, base_clock_ghz=3.3, tdp_w=53, memory_type="DDR3")),
    ("G1830",          dict(cores=2, threads=2, base_clock_ghz=2.8, tdp_w=53, memory_type="DDR3")),

    # ── AMD Ryzen 9000 series (AM5) ───────────────────────────────────────────
    ("RYZEN 9 9950X3D", dict(cores=16, threads=32, base_clock_ghz=4.3, boost_clock_ghz=5.7, tdp_w=170, memory_type="DDR5")),
    ("RYZEN 9 9950X",   dict(cores=16, threads=32, base_clock_ghz=4.3, boost_clock_ghz=5.7, tdp_w=170, memory_type="DDR5")),
    ("RYZEN 9 9900X3D", dict(cores=12, threads=24, base_clock_ghz=4.4, boost_clock_ghz=5.5, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 9 9900X",   dict(cores=12, threads=24, base_clock_ghz=4.4, boost_clock_ghz=5.6, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 9 9900",    dict(cores=12, threads=24, base_clock_ghz=3.7, boost_clock_ghz=5.4, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 7 9700X",   dict(cores=8,  threads=16, base_clock_ghz=3.8, boost_clock_ghz=5.5, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 7 9800X3D", dict(cores=8,  threads=16, base_clock_ghz=4.7, boost_clock_ghz=5.2, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 7 9800X",   dict(cores=8,  threads=16, base_clock_ghz=4.7, boost_clock_ghz=5.2, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 5 9600X",   dict(cores=6,  threads=12, base_clock_ghz=3.9, boost_clock_ghz=5.4, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 5 9600",    dict(cores=6,  threads=12, base_clock_ghz=3.8, boost_clock_ghz=5.1, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 5 9500F",   dict(cores=6,  threads=12, base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=65,  memory_type="DDR5")),

    # ── AMD Ryzen 8000G series (AM5, integrated graphics) ────────────────────
    ("RYZEN 7 8700G",   dict(cores=8, threads=16, base_clock_ghz=4.2, boost_clock_ghz=5.1, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 7 8700F",   dict(cores=8, threads=16, base_clock_ghz=4.1, boost_clock_ghz=5.0, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 5 8600G",   dict(cores=6, threads=12, base_clock_ghz=4.3, boost_clock_ghz=5.0, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 5 8500G",   dict(cores=6, threads=12, base_clock_ghz=3.5, boost_clock_ghz=5.0, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 7 PRO 8700G", dict(cores=8, threads=16, base_clock_ghz=4.2, boost_clock_ghz=5.1, tdp_w=65, memory_type="DDR5")),

    # ── AMD Ryzen 7000 series (AM5) ───────────────────────────────────────────
    ("RYZEN 9 7950X",   dict(cores=16, threads=32, base_clock_ghz=4.5, boost_clock_ghz=5.7, tdp_w=170, memory_type="DDR5")),
    ("RYZEN 9 7900X",   dict(cores=12, threads=24, base_clock_ghz=4.7, boost_clock_ghz=5.6, tdp_w=170, memory_type="DDR5")),
    ("RYZEN 9 7900",    dict(cores=12, threads=24, base_clock_ghz=3.7, boost_clock_ghz=5.4, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 7 7700X",   dict(cores=8,  threads=16, base_clock_ghz=4.5, boost_clock_ghz=5.4, tdp_w=105, memory_type="DDR5")),
    ("RYZEN 7 7700",    dict(cores=8,  threads=16, base_clock_ghz=3.8, boost_clock_ghz=5.3, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 7 7800X3D", dict(cores=8,  threads=16, base_clock_ghz=4.5, boost_clock_ghz=5.0, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 5 7600X",   dict(cores=6,  threads=12, base_clock_ghz=4.7, boost_clock_ghz=5.3, tdp_w=105, memory_type="DDR5")),
    ("RYZEN 5 7600",    dict(cores=6,  threads=12, base_clock_ghz=3.8, boost_clock_ghz=5.1, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 5 7500X3D", dict(cores=6,  threads=12, base_clock_ghz=4.0, boost_clock_ghz=4.5, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 5 7500X",   dict(cores=6,  threads=12, base_clock_ghz=4.0, boost_clock_ghz=5.0, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 5 7500F",   dict(cores=6,  threads=12, base_clock_ghz=3.7, boost_clock_ghz=5.0, tdp_w=65,  memory_type="DDR5")),
    ("RYZEN 7 7800X",   dict(cores=8,  threads=16, base_clock_ghz=4.5, boost_clock_ghz=5.0, tdp_w=120, memory_type="DDR5")),
    ("RYZEN 5 7400",    dict(cores=6,  threads=12, base_clock_ghz=4.3, boost_clock_ghz=4.7, tdp_w=65,  memory_type="DDR5")),
    # PRO variants
    ("RYZEN 9 PRO 7945", dict(cores=12, threads=24, base_clock_ghz=3.7, boost_clock_ghz=5.4, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 7 PRO 9745", dict(cores=12, threads=24, base_clock_ghz=4.0, boost_clock_ghz=5.1, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 7 PRO 7745", dict(cores=8,  threads=16, base_clock_ghz=3.8, boost_clock_ghz=5.3, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 5 PRO 9645", dict(cores=6,  threads=12, base_clock_ghz=4.3, boost_clock_ghz=5.2, tdp_w=65, memory_type="DDR5")),
    ("RYZEN 5 PRO 8600G", dict(cores=6, threads=12, base_clock_ghz=4.3, boost_clock_ghz=5.0, tdp_w=65, memory_type="DDR5")),

    # ── AMD Ryzen 5000 series (AM4) ───────────────────────────────────────────
    ("RYZEN 9 5950X",   dict(cores=16, threads=32, base_clock_ghz=3.4, boost_clock_ghz=4.9, tdp_w=105, memory_type="DDR4")),
    ("RYZEN 9 5900X",   dict(cores=12, threads=24, base_clock_ghz=3.7, boost_clock_ghz=4.8, tdp_w=105, memory_type="DDR4")),
    ("RYZEN 9 5900",    dict(cores=12, threads=24, base_clock_ghz=3.0, boost_clock_ghz=4.7, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 7 5800X3D", dict(cores=8,  threads=16, base_clock_ghz=3.4, boost_clock_ghz=4.5, tdp_w=105, memory_type="DDR4")),
    ("RYZEN 7 5800X",   dict(cores=8,  threads=16, base_clock_ghz=3.8, boost_clock_ghz=4.7, tdp_w=105, memory_type="DDR4")),
    ("RYZEN 7 5800",    dict(cores=8,  threads=16, base_clock_ghz=3.4, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 7 5700X3D", dict(cores=8,  threads=16, base_clock_ghz=3.0, boost_clock_ghz=4.1, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 7 5700X",   dict(cores=8,  threads=16, base_clock_ghz=3.4, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 7 5700G",   dict(cores=8,  threads=16, base_clock_ghz=3.8, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 7 5700",    dict(cores=8,  threads=16, base_clock_ghz=3.7, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 5600X",   dict(cores=6,  threads=12, base_clock_ghz=3.7, boost_clock_ghz=4.6, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 5600G",   dict(cores=6,  threads=12, base_clock_ghz=3.9, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 5600",    dict(cores=6,  threads=12, base_clock_ghz=3.5, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 5500",    dict(cores=6,  threads=12, base_clock_ghz=3.6, boost_clock_ghz=4.2, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 5500GT",  dict(cores=6,  threads=12, base_clock_ghz=3.6, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 3 5300G",   dict(cores=4,  threads=8,  base_clock_ghz=4.0, boost_clock_ghz=4.2, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 3 5300",    dict(cores=4,  threads=8,  base_clock_ghz=3.6, boost_clock_ghz=4.2, tdp_w=65,  memory_type="DDR4")),

    # ── AMD Ryzen 4000 series (AM4) ───────────────────────────────────────────
    ("RYZEN 5 4500",    dict(cores=6, threads=12, base_clock_ghz=3.6, boost_clock_ghz=4.1, tdp_w=65, memory_type="DDR4")),
    ("RYZEN 3 4100",    dict(cores=4, threads=8,  base_clock_ghz=3.8, boost_clock_ghz=4.0, tdp_w=65, memory_type="DDR4")),
    ("RYZEN 3 3200G",   dict(cores=4, threads=4,  base_clock_ghz=3.6, boost_clock_ghz=4.0, tdp_w=65, memory_type="DDR4")),

    # ── AMD Ryzen 3000 series (AM4) ───────────────────────────────────────────
    ("RYZEN 9 3900X",   dict(cores=12, threads=24, base_clock_ghz=3.8, boost_clock_ghz=4.6, tdp_w=105, memory_type="DDR4")),
    ("RYZEN 7 3700X",   dict(cores=8,  threads=16, base_clock_ghz=3.6, boost_clock_ghz=4.4, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 5 3600",    dict(cores=6,  threads=12, base_clock_ghz=3.6, boost_clock_ghz=4.2, tdp_w=65,  memory_type="DDR4")),
    ("RYZEN 3 1200 AF", dict(cores=4,  threads=4,  base_clock_ghz=3.1, boost_clock_ghz=3.4, tdp_w=65,  memory_type="DDR4")),

    # ── AMD Threadripper Pro 9000 (sTR5) ─────────────────────────────────────
    ("THREADRIPPER PRO 9995WX", dict(cores=96, threads=192, base_clock_ghz=3.0, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 9975WX", dict(cores=64, threads=128, base_clock_ghz=3.3, boost_clock_ghz=5.0, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 9965WX", dict(cores=48, threads=96,  base_clock_ghz=3.5, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 9955WX", dict(cores=32, threads=64,  base_clock_ghz=3.6, boost_clock_ghz=5.0, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER 9980X",      dict(cores=64, threads=128, base_clock_ghz=3.2, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER 7970X",      dict(cores=32, threads=64,  base_clock_ghz=4.0, boost_clock_ghz=5.3, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER 7980X",      dict(cores=64, threads=128, base_clock_ghz=3.2, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER 7960X",      dict(cores=24, threads=48,  base_clock_ghz=4.2, boost_clock_ghz=5.3, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 7995WX", dict(cores=96, threads=192, base_clock_ghz=2.5, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 7985WX", dict(cores=64, threads=128, base_clock_ghz=3.2, boost_clock_ghz=5.1, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 7975WX", dict(cores=32, threads=64,  base_clock_ghz=4.0, boost_clock_ghz=5.3, tdp_w=350, memory_type="DDR5")),
    ("THREADRIPPER PRO 7965WX", dict(cores=24, threads=48,  base_clock_ghz=4.2, boost_clock_ghz=5.3, tdp_w=350, memory_type="DDR5")),
    # Threadripper Pro 5000 (WRX80)
    ("THREADRIPPER PRO 5995WX", dict(cores=64, threads=128, base_clock_ghz=2.7, boost_clock_ghz=4.5, tdp_w=280, memory_type="DDR4")),

    # ── AMD Athlon / legacy ───────────────────────────────────────────────────
    ("A6-SERIES X2 5400K",     dict(cores=2, threads=2, base_clock_ghz=3.6, tdp_w=65, memory_type="DDR3")),
    ("A6 5400K",               dict(cores=2, threads=2, base_clock_ghz=3.6, tdp_w=65, memory_type="DDR3")),
]

# ── GPU reference ─────────────────────────────────────────────────────────────
# Key: normalised model string fragment (uppercase, matched with str.upper())
# Value: dict of fields — only non-None values will be written to DB
#
# Fields: memory_type, pcie_version, recommended_psu_w
# (length_mm is manufacturer-specific — not stored here)

GPU_SPECS: list[tuple[str, dict]] = [
    # ── NVIDIA Blackwell (RTX 50) ─────────────────────────────────────────────
    ("RTX 5090",       dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=1000)),
    ("RTX 5080",       dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=850)),
    ("RTX 5070 TI",    dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=750)),
    ("RTX 5070 TI",    dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=750)),
    ("RTX 5070",       dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=650)),
    ("RTX 5060 TI",    dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=600)),
    ("RTX 5060",       dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=550)),
    ("RTX 5050",       dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=550)),
    # Workstation Blackwell Pro
    ("RTX PRO 6000",   dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=450)),
    ("RTX PRO 4000",   dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=300)),
    ("RTX PRO 2000",   dict(memory_type="GDDR7", pcie_version="5.0", recommended_psu_w=200)),

    # ── NVIDIA Ada Lovelace (RTX 40) ─────────────────────────────────────────
    ("RTX 4090",       dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=850)),
    ("RTX 4080 SUPER", dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=750)),
    ("RTX 4080",       dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=750)),
    ("RTX 4070 TI SUPER", dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=700)),
    ("RTX 4070 TI",    dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=700)),
    ("RTX 4070 SUPER", dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=650)),
    ("RTX 4070",       dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=650)),
    ("RTX 4060 TI",    dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=550)),
    ("RTX 4060",       dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=550)),
    ("RTX 4050",       dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=450)),

    # ── NVIDIA Ampere (RTX 30) ────────────────────────────────────────────────
    ("RTX 3090 TI",    dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=850)),
    ("RTX 3090",       dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=750)),
    ("RTX 3080 TI",    dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=750)),
    ("RTX 3080",       dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=750)),
    ("RTX 3070 TI",    dict(memory_type="GDDR6X", pcie_version="4.0", recommended_psu_w=650)),
    ("RTX 3070",       dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=650)),
    ("RTX 3060 TI",    dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=600)),
    ("RTX 3060",       dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=550)),
    ("RTX 3050",       dict(memory_type="GDDR6",  pcie_version="4.0", recommended_psu_w=450)),
    ("RTX 2060 SUPER", dict(memory_type="GDDR6",  pcie_version="3.0", recommended_psu_w=550)),
    ("RTX 2060",       dict(memory_type="GDDR6",  pcie_version="3.0", recommended_psu_w=500)),

    # ── NVIDIA Turing / Pascal / older ────────────────────────────────────────
    ("GTX 1660 TI SUPER", dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=450)),
    ("GTX 1660 TI",       dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=450)),
    ("GTX 1660 SUPER",    dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=450)),
    ("GTX 1660",          dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=450)),
    ("GTX 1650 SUPER",    dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=350)),
    ("GTX 1650",          dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("GTX 1630",          dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=300)),
    ("GTX 1050 TI",       dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("GTX 1050",          dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("GT 710",            dict(memory_type="GDDR5", pcie_version="2.0", recommended_psu_w=300)),
    ("GT 730",            dict(memory_type="GDDR5", pcie_version="2.0", recommended_psu_w=300)),
    ("GT 740",            dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("GT 1030",           dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("GT 610",            dict(memory_type="GDDR3", pcie_version="2.0", recommended_psu_w=300)),
    ("GT 210",            dict(memory_type="GDDR3", pcie_version="2.0", recommended_psu_w=300)),
    ("GT 240",            dict(memory_type="GDDR5", pcie_version="2.0", recommended_psu_w=300)),

    # ── AMD RDNA 4 (RX 9000) ─────────────────────────────────────────────────
    ("RX 9070 XT",     dict(memory_type="GDDR6", pcie_version="5.0", recommended_psu_w=850)),
    ("RX 9070",        dict(memory_type="GDDR6", pcie_version="5.0", recommended_psu_w=700)),
    ("RX 9060 XT",     dict(memory_type="GDDR6", pcie_version="5.0", recommended_psu_w=450)),

    # ── AMD RDNA 3 (RX 7000) ─────────────────────────────────────────────────
    ("RX 7900 XTX",    dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=800)),
    ("RX 7900 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=800)),
    ("RX 7900 GRE",    dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=700)),
    ("RX 7800 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=700)),
    ("RX 7700 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=600)),
    ("RX 7600 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("RX 7600",        dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),

    # ── AMD RDNA 2 (RX 6000) ─────────────────────────────────────────────────
    ("RX 6950 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=850)),
    ("RX 6900 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=850)),
    ("RX 6800 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=750)),
    ("RX 6800",        dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=650)),
    ("RX 6700 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=650)),
    ("RX 6700",        dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=650)),
    ("RX 6650 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("RX 6600 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=500)),
    ("RX 6600",        dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=500)),
    ("RX 6500 XT",     dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=400)),
    ("RX 6400",        dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=400)),

    # ── AMD older ─────────────────────────────────────────────────────────────
    ("RX 580",         dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=500)),
    ("RX 570",         dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=450)),
    ("RX 560",         dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=400)),
    ("RX 550",         dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=350)),
    ("RX5500",         dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=450)),
    ("R5 230",         dict(memory_type="DDR3",  pcie_version="2.0", recommended_psu_w=300)),

    # ── Intel Arc ─────────────────────────────────────────────────────────────
    ("ARC B580",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("ARC B570",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("ARC A770",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=600)),
    ("ARC A750",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("ARC A580",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=550)),
    ("ARC A380",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=350)),
    ("ARC A310",       dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),

    # ── Workstation / Quadro ──────────────────────────────────────────────────
    ("QUADRO RTX A4000", dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),
    ("QUADRO RTX A2000", dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),
    ("QUADRO RTX A1000", dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),
    ("QUADRO RTX A400",  dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),
    ("QUADRO T1000",     dict(memory_type="GDDR6", pcie_version="3.0", recommended_psu_w=300)),
    ("QUADRO P400",      dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
    ("RADEON PRO W7700", dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=450)),
    ("RADEON PRO W7500", dict(memory_type="GDDR6", pcie_version="4.0", recommended_psu_w=300)),
    ("RADEON PRO WX 3200", dict(memory_type="GDDR5", pcie_version="3.0", recommended_psu_w=300)),
]


def _norm(s: str) -> str:
    """Uppercase + strip spaces/hyphens for compact matching (e.g. 'RTX4060TI')."""
    return s.upper().replace(" ", "").replace("-", "")


def lookup_cpu(model: str) -> dict:
    """Return reference spec fields for a CPU model string. Never raises."""
    if not model:
        return {}
    m      = model.upper().strip()
    m_cmp  = _norm(model)
    for key, specs in CPU_SPECS:
        k     = key.upper()
        k_cmp = _norm(key)
        if k in m or k_cmp in m_cmp:
            return {k: v for k, v in specs.items() if v is not None}
    return {}


def lookup_gpu(model: str) -> dict:
    """Return reference spec fields for a GPU model string. Never raises."""
    if not model:
        return {}
    m      = model.upper().strip()
    m_cmp  = _norm(model)
    # Longer / more-specific keys should match first — sort by length desc
    candidates = sorted(GPU_SPECS, key=lambda t: len(t[0]), reverse=True)
    for key, specs in candidates:
        k     = key.upper()
        k_cmp = _norm(key)
        if k in m or k_cmp in m_cmp:
            return {k: v for k, v in specs.items() if v is not None}
    return {}
