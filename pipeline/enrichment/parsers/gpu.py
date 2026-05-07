import re

from enrichment.fetch import fetch_spec_text

NON_GPU_WORDS = ["wireview", "contact frame", "bracket", "adapter", "measuring", "holder", "mount", "riser cable", "кабел", "кабло", "hdmi кабел", "dp кабел"]

# Full-prefixed patterns — searched first so they win over compact SKU codes like "RTX5080-O16G"
_GPU_FULL_RE = (
    r"GeForce\s+RTX\s*[™®]?\s*\d{3,4}\s*(?:Ti\s+SUPER|Ti|SUPER)?"
    r"|Radeon\s*[™®]?\s+RX\s*\d{3,4}\s*(?:XTX|XT)?"
    # Workstation — prefixed forms
    r"|Quadro\s+RTX\s+A\d{3,4}"        # Quadro RTX A4000, RTX A1000
    r"|Quadro\s+[TP]\d{3,4}[A-Z]?"     # Quadro T1000, Quadro P400
    r"|RTX\s+(?:Pro\s+)?\d{3,4}[A-Z]?" # RTX Pro 4000, RTX A4000, RTX A400
    r"|Radeon\s+Pro\s+W[XG]?\s*\d{3,4}" # Radeon Pro W7700, Radeon Pro WX 3200
    r"|Arc\s+[AB]\d{3,4}"              # Arc A770, Arc A380, Arc B580
)
# Compact patterns — used when no full-prefixed match is found, and for title-only parsing
_GPU_COMPACT_RE = (
    r"RTX\s*\d{3,4}\s*(?:Ti\s+SUPER|Ti|SUPER)?"
    r"|RX\s*\d{3,4}\s*(?:XTX|XT)?"
    r"|GTX\s*\d{3,4}\s*(?:Ti\s+Super|Ti|Super)?"
    r"|GT\s*\d{3,4}"
)
# Combined pattern used for title-only extraction
_GPU_MODEL_RE = _GPU_FULL_RE + "|" + _GPU_COMPACT_RE


def parse(title: str, url: str | None = None) -> dict | None:
    title_lower = (title or "").lower()
    if any(w in title_lower for w in NON_GPU_WORDS):
        return None

    text = fetch_spec_text(url) if url else None

    if text:
        gpu = _parse_from_page(title, text)
        # Gjirafa spec pages often omit VRAM GB — fall back to title
        if gpu.get("vram_gb") is None:
            title_gpu = _parse_from_title(title)
            if title_gpu and title_gpu.get("vram_gb") is not None:
                gpu["vram_gb"] = title_gpu["vram_gb"]
                if gpu.get("memory_type") is None:
                    gpu["memory_type"] = title_gpu.get("memory_type")
        return gpu
    return _parse_from_title(title)


def _parse_from_page(title: str, text: str) -> dict:
    gpu = {}

    # Try full prefixed name first (avoids matching compact SKU codes like "RTX5080-O16G")
    m = re.search(rf"({_GPU_FULL_RE})", text, re.IGNORECASE)
    if not m:
        m = re.search(rf"({_GPU_COMPACT_RE})", text, re.IGNORECASE)
    if not m:
        m = re.search(rf"({_GPU_MODEL_RE})", title, re.IGNORECASE)
    gpu["gpu_model"] = re.sub(r"[™®]", "", m.group(1)).strip() if m else None

    # VRAM — Anhoch: "Memory Size: 6 GB", generic: "16 GB GDDR6"
    m = re.search(
        r"(?:Memory\s+Size(?:/Bus)?\s*:\s*(\d+)\s*GB"
        r"|\bMemory\s*:\s*(\d+)\s*GB)",
        text, re.IGNORECASE,
    )
    if m:
        gpu["vram_gb"] = int(m.group(1) or m.group(2))
    else:
        # Search for GB value near GDDR/HBM mention (handles "16 GB брза GDDR7" style text)
        gddr_m = re.search(r"(GDDR|HBM)\S*", text, re.IGNORECASE)
        if gddr_m:
            vicinity = text[max(0, gddr_m.start() - 60): gddr_m.end() + 60]
            m = re.search(r"\b(\d+)\s*GB\b", vicinity, re.IGNORECASE)
        else:
            m = re.search(r"\b(\d+)\s*GB\b", text, re.IGNORECASE)
        gpu["vram_gb"] = int(m.group(1)) if m else None

    m = re.search(r"(GDDR\d+X?)", text, re.IGNORECASE)
    gpu["memory_type"] = m.group(1).upper() if m else None

    m = re.search(
        r"(?:PCI[- ]?E(?:xpress)?\s*[:\-]?\s*(\d\.\d)"
        r"|Card\s+Bus\s*:\s*PCI-?E\s*(\d\.\d))",
        text, re.IGNORECASE,
    )
    gpu["pcie_version"] = (m.group(1) or m.group(2)) if m else None

    m = re.search(
        r"(?:L\s*=\s*(\d+)"
        r"|Dimension\s*\(L\)\s*:\s*(\d+)"
        r"|Card\s+Dimension\s*\(mm\)\s*:\s*(\d+)"
        r"|Card\s+size.*?L\s*=\s*(\d+))",
        text, re.IGNORECASE,
    )
    gpu["length_mm"] = int(next(g for g in m.groups() if g is not None)) if m else None

    m = re.search(
        r"(?:Recommended\s+PSU\s*:\s*(\d+)\s*W"
        r"|Minimum\s+(\d+)\s*W(?:att)?\s+Power"
        r"|Recommended\s*:\s*PSU\s*(\d+)\s*W)",
        text, re.IGNORECASE,
    )
    gpu["recommended_psu_w"] = int(next(g for g in m.groups() if g is not None)) if m else None

    return gpu


def _parse_from_title(title: str) -> dict | None:
    """Title-only extraction for stores with no spec page (Setec)."""
    gpu = {
        "gpu_model": None, "vram_gb": None, "memory_type": None,
        "pcie_version": None, "length_mm": None, "recommended_psu_w": None,
    }

    m = re.search(rf"({_GPU_MODEL_RE})", title, re.IGNORECASE)
    if m:
        gpu["gpu_model"] = re.sub(r"[™®]", "", m.group(1)).strip()

    # VRAM: ASUS "OXG" code — O32G=32GB, O4GD6=4GB
    m = re.search(r"\bO(\d+)G(?:D|$)", title, re.IGNORECASE)
    if m:
        gpu["vram_gb"] = int(m.group(1))
    if gpu["vram_gb"] is None:
        m = re.search(r"\b(\d+)\s*GB\b", title, re.IGNORECASE)
        if m:
            gpu["vram_gb"] = int(m.group(1))
    # Compact "-4G", "-12G" suffix (no "GB")
    if gpu["vram_gb"] is None:
        m = re.search(r"-(\d{1,2})G\b", title, re.IGNORECASE)
        if m:
            gpu["vram_gb"] = int(m.group(1))

    m = re.search(r"(GDDR\d+X?)", title, re.IGNORECASE)
    gpu["memory_type"] = m.group(1).upper() if m else None

    return gpu if gpu["vram_gb"] is not None else None
