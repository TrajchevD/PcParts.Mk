import re

from enrichment.fetch import fetch_spec_text

# Full name variants (Anhoch) + compact variants without "Core" (Setec)
CPU_MODEL_RE = (
    r"Intel\s+Core\s+i[3579]\s*[- ]?\s*\d{4,5}(?:KS|KF|K|F)?"
    r"|Intel\s+Core\s+Ultra\s+[3579]\s*\d{3}[A-Z]?"
    r"|AMD\s+Ryzen\s+Threadripper\s+(?:PRO\s+)?\d{4}[A-Z]*"   # Threadripper / Threadripper PRO
    r"|AMD\s+Ryzen\s+[3579]\s*(?:PRO\s+)?\d+(?:\s*(?:AF|X3D|3D|X|G|F))?"
    r"|Intel\s+i[3579][- ]?\d{4,5}(?:KS|KF|K|F)?"     # Setec: "Intel i9-14900K"
    r"|Intel\s+(?:Pentium|Celeron)\s+(?:Gold\s+|Silver\s+)?[GJ]\d{4,5}[A-Z]?"  # Pentium/Celeron G-series
)

NON_CPU_WORDS = ["contact", "frame", "bracket", "holder", "mount"]


def parse(title: str, url: str | None = None) -> dict | None:
    if any(w in (title or "").lower() for w in NON_CPU_WORDS):
        return None

    text = fetch_spec_text(url) if url else None

    cpu = {
        "cpu_model": None, "brand": None, "socket": None,
        "cores": None, "threads": None, "base_clock_ghz": None,
        "boost_clock_ghz": None, "tdp_w": None, "memory_type": None,
    }

    # Model — title first, then spec text, then URL slug
    sources = [title or ""]
    if text:
        sources.append(text)
    if url:
        sources.append(url.split("/")[-1].replace("-", " "))
    for source in sources:
        m = re.search(rf"({CPU_MODEL_RE})", source, re.IGNORECASE)
        if m:
            cpu["cpu_model"] = re.sub(r"[™®]", "", m.group(1)).strip()
            cpu["brand"] = "Intel" if "intel" in cpu["cpu_model"].lower() else "AMD"
            break

    if not text:
        # No spec page (Setec) — extract what we can from title
        _extract_from_title(cpu, title or "")
        return cpu if cpu["cpu_model"] else None

    # Socket
    m = re.search(r"(?:CPU\s+)?Socket\s*:\s*(AM[45]|LGA\s*\d+)", text, re.IGNORECASE)
    if m:
        cpu["socket"] = m.group(1).replace(" ", "").upper()
    if not cpu["socket"]:
        m = re.search(r"\bFC?LGA\s*(\d{4})\b", text, re.IGNORECASE)
        if m:
            cpu["socket"] = f"LGA{m.group(1)}"
    if not cpu["socket"]:
        m = re.search(r"\b(AM[45]|LGA\s*\d{4})(?!\d)", text, re.IGNORECASE)
        if m:
            cpu["socket"] = m.group(1).replace(" ", "").upper()
    if not cpu["socket"]:
        m = re.search(r"\b(AM[45]|LGA\s*\d+)(?!\d)", title or "", re.IGNORECASE)
        if m:
            cpu["socket"] = m.group(1).replace(" ", "").upper()

    # Cores — Anhoch: "# of CPU Cores" / Neptun: "CPU Cores"
    m = re.search(r"(?:#\s+of\s+CPU\s+Cores|Total\s+Cores|CPU\s+Cores)\s*:\s*(\d+)", text, re.IGNORECASE)
    if m:
        cpu["cores"] = int(m.group(1))

    # Threads — Anhoch: "# of Threads" / Neptun: "Threads"
    m = re.search(r"(?:#\s+of\s+Threads|Total\s+Threads|(?<!\w)Threads)\s*:\s*(\d+)", text, re.IGNORECASE)
    if m:
        cpu["threads"] = int(m.group(1))

    # Base clock
    m = re.search(r"(?:Base\s+Clock|Base\s+Frequency)\s*:\s*([\d.]+)\s*GHz", text, re.IGNORECASE)
    if m:
        cpu["base_clock_ghz"] = float(m.group(1))
    if cpu["base_clock_ghz"] is None:
        # Gjirafa MK: "Основна фреквенција [GHz]: 3.9" (base frequency in Macedonian)
        m = re.search(r"[Оо]сновна\s+фреквенција\s*\[GHz\]\s*:\s*([\d.]+)", text)
        if m:
            cpu["base_clock_ghz"] = float(m.group(1))
    if cpu["base_clock_ghz"] is None:
        m = re.search(r"(\d+(?:\.\d+)?)\s*GHz", title or "")
        if m:
            cpu["base_clock_ghz"] = float(m.group(1))

    # Boost clock
    m = re.search(r"Max\s*\.?\s*Boost\s+Clock\s*:?\s*(?:Up\s+to\s+)?([\d.]+)\s*GHz", text, re.IGNORECASE)
    if not m:
        m = re.search(r"Max\s+Turbo\s+Frequency\s*:\s*([\d.]+)\s*GHz", text, re.IGNORECASE)
    if not m:
        # Gjirafa MK: "Максимална турбо фреквенција [GHz]: 5.2"
        m = re.search(r"[Мм]аксимална\s+турбо\s+фреквенција\s*\[GHz\]\s*:\s*([\d.]+)", text)
    if m:
        cpu["boost_clock_ghz"] = float(m.group(1))

    # Cores / Threads
    if cpu["cores"] is None:
        # Gjirafa MK: "Број на јадра / влакна: 8/16"
        m = re.search(r"[Бб]рој\s+на\s+јадра\s*/\s*влакна\s*:\s*(\d+)\s*/\s*(\d+)", text)
        if m:
            cpu["cores"]   = int(m.group(1))
            cpu["threads"] = int(m.group(2))

    # TDP
    m = re.search(r"(?:Default\s+TDP|Processor\s+Base\s+Power).*?(\d+)\s*W", text, re.IGNORECASE)
    if m:
        cpu["tdp_w"] = int(m.group(1))

    # Memory type — Anhoch: "System Memory Type" / Neptun: "Memory Type"
    m = re.search(r"(?:System\s+)?Memory\s+Types?\s*[:\-]\s*(DDR\d)", text, re.IGNORECASE)
    if m:
        cpu["memory_type"] = m.group(1).upper()
    if not cpu["memory_type"]:
        m = re.search(r"\b(DDR[345])\b", title or "", re.IGNORECASE)
        if m:
            cpu["memory_type"] = m.group(1).upper()

    # Socket inference fallback — if spec text had no explicit socket, infer from model name
    if not cpu["socket"] and cpu["cpu_model"]:
        cpu["socket"] = _infer_socket(cpu["cpu_model"])

    return cpu


def _extract_from_title(cpu: dict, title: str) -> None:
    """Best-effort extraction from title alone (Setec — no spec page available)."""
    # Socket from title text
    m = re.search(r"\b(AM[45]|LGA\s*\d+)(?!\d)", title, re.IGNORECASE)
    if m:
        cpu["socket"] = m.group(1).replace(" ", "").upper()

    # Infer socket from model if not in title
    if not cpu["socket"] and cpu["cpu_model"]:
        cpu["socket"] = _infer_socket(cpu["cpu_model"])

    m = re.search(r"\b(DDR[345])\b", title, re.IGNORECASE)
    if m:
        cpu["memory_type"] = m.group(1).upper()

    m = re.search(r"([\d.]+)\s*GHz", title)
    if m:
        cpu["base_clock_ghz"] = float(m.group(1))


def _infer_socket(model: str) -> str | None:
    """Infer CPU socket from model name when not stated explicitly."""
    m = model.upper()
    if "ULTRA" in m:
        return "LGA1851"   # Intel Arrow Lake / Lunar Lake
    # Intel iX — infer from generation (first 2 digits of model number)
    g = re.search(r"\bI[3579][- ]?(\d{1,2})\d{3}", m)
    if g:
        gen = int(g.group(1))
        if gen >= 12:
            return "LGA1700"
        if gen in (10, 11):
            return "LGA1200"
        if gen in (8, 9):
            return "LGA1151"
        return None
    # Intel Pentium/Celeron G-series — all modern ones use LGA1700 (12th gen+) or LGA1200/LGA1151
    if re.search(r"\b(?:PENTIUM|CELERON)\b", m):
        g = re.search(r"\b[GJ](\d)(\d{3,4})", m)
        if g:
            prefix = int(g.group(1))
            if prefix >= 7:
                return "LGA1700"
            if prefix in (5, 6):
                return "LGA1200"
            return "LGA1151"
        return None
    # AMD Ryzen Threadripper — 7000+ series uses sTR5, 5000 PRO uses WRX80
    if "THREADRIPPER" in m:
        t = re.search(r"THREADRIPPER\s+(?:PRO\s+)?(\d)", m)
        if t:
            gen = int(t.group(1))
            if gen >= 7:
                return "sTR5"
            if gen == 5 and "PRO" in m:
                return "WRX80"
        return None
    # AMD Ryzen — infer from series digit (skip optional PRO between rank and number)
    r = re.search(r"RYZEN\s+[3579]\s*(?:PRO\s+)?(\d)\d{3}", m)
    if r:
        series = int(r.group(1))
        return "AM5" if series >= 7 else "AM4"
    return None
