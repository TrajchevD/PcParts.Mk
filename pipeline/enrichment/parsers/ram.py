import re

from normalizer import _preprocess

KNOWN_BRANDS = [
    "Kingston", "Corsair", "G.Skill", "Crucial", "ADATA", "Adata",
    "Geil", "Patriot", "TeamGroup", "Team", "HP", "Samsung",
    "Micron", "PNY", "Goodram",
]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse(title: str, url: str | None = None) -> dict | None:
    t = _norm(_preprocess(title or ""))

    memory_type = None
    m = re.search(r"\bDDR[345]L?\b", t, re.IGNORECASE)
    if m:
        memory_type = re.sub(r"L$", "", m.group(0), flags=re.IGNORECASE).upper()

    total_capacity_gb = None
    m = re.search(r"\b(\d+)\s*GB\b", t, re.IGNORECASE)
    if m:
        total_capacity_gb = int(m.group(1))

    speed_mhz = None
    m = re.search(r"\b(\d{4,5})\s*(?:MHz|MT/s)\b", t, re.IGNORECASE)
    if not m:
        m = re.search(r"\bDDR[345][-/](\d{4,5})\b", t, re.IGNORECASE)
    if m:
        speed_mhz = int(m.group(1))

    cas_latency = None
    m = re.search(r"\bCL\s*(\d{2})\b", t, re.IGNORECASE)
    if m:
        cas_latency = int(m.group(1))

    sticks = 1
    capacity_per_stick_gb = None

    m = re.search(r"\b(\d+)\s*x\s*(\d+)\s*GB\b", t, re.IGNORECASE)
    if m:
        sticks = int(m.group(1))
        per = int(m.group(2))
        total_capacity_gb = total_capacity_gb or (sticks * per)
        capacity_per_stick_gb = per
    else:
        m = re.search(r"\((\d+)\s*x\s*(\d+)\)", t, re.IGNORECASE)
        if m:
            sticks = int(m.group(1))
            per = int(m.group(2))
            total_capacity_gb = total_capacity_gb or (sticks * per)
            capacity_per_stick_gb = per

    if capacity_per_stick_gb is None and total_capacity_gb and sticks:
        if total_capacity_gb % sticks == 0:
            capacity_per_stick_gb = total_capacity_gb // sticks

    ecc  = bool(re.search(r"\bECC\b",  t, re.IGNORECASE))
    expo = bool(re.search(r"\bEXPO\b", t, re.IGNORECASE))
    xmp  = bool(re.search(r"\bXMP\b",  t, re.IGNORECASE))

    brand = None
    for b in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", t, re.IGNORECASE):
            brand = "ADATA" if b.lower() == "adata" else b
            break

    series = None
    if brand:
        after = re.split(rf"\b{re.escape(brand)}\b", t, flags=re.IGNORECASE)
        if len(after) > 1:
            s = re.split(
                r"\b(CL\d+|DDR[45]|\d{4,5}(?:MHz|MT/s)|\d+\s*GB|Kit|ECC|EXPO|XMP|Bulk|Server)\b",
                after[1], maxsplit=1, flags=re.IGNORECASE,
            )[0]
            series = re.sub(r'[,\s]+$', '', _norm(s)) or None

    result = {
        "brand": brand, "series": series, "memory_type": memory_type,
        "total_capacity_gb": total_capacity_gb, "sticks": sticks,
        "capacity_per_stick_gb": capacity_per_stick_gb, "speed_mhz": speed_mhz,
        "cas_latency": cas_latency, "expo": int(expo), "xmp": int(xmp), "ecc": int(ecc),
    }

    # Enrich from spec page when URL is available
    if url:
        try:
            from enrichment.fetch import fetch_spec_text
            text = fetch_spec_text(url)
            if text:
                result = _enrich_from_text(result, text)
        except Exception:
            pass

    return result


def _enrich_from_text(result: dict, text: str) -> dict:
    """Override/supplement title-parsed values with data from the spec page."""
    t = text

    # Memory type
    if result["memory_type"] is None:
        m = re.search(r"\b(DDR[345])\b", t, re.IGNORECASE)
        if m:
            result["memory_type"] = m.group(1).upper()

    # Total capacity — take the largest GB value seen
    caps = [int(x) for x in re.findall(r"\b(\d+)\s*GB\b", t, re.IGNORECASE)]
    if caps and result["total_capacity_gb"] is None:
        result["total_capacity_gb"] = max(caps)

    # Kit notation: "2 x 16GB", "4 x 8GB", "2x16"
    m = re.search(r"\b(\d+)\s*[xX×]\s*(\d+)\s*GB\b", t)
    if m:
        sticks = int(m.group(1))
        per    = int(m.group(2))
        if result["sticks"] == 1:
            result["sticks"] = sticks
        if result["capacity_per_stick_gb"] is None:
            result["capacity_per_stick_gb"] = per
        if result["total_capacity_gb"] is None:
            result["total_capacity_gb"] = sticks * per
    else:
        m = re.search(r"\bKit\s+of\s+(\d+)\b", t, re.IGNORECASE)
        if m and result["sticks"] == 1:
            result["sticks"] = int(m.group(1))

    # Speed
    if result["speed_mhz"] is None:
        m = re.search(r"\b(\d{4,5})\s*(?:MHz|MT/s)\b", t, re.IGNORECASE)
        if not m:
            m = re.search(r"\bDDR[345][-/](\d{4,5})\b", t, re.IGNORECASE)
        if m:
            result["speed_mhz"] = int(m.group(1))

    # CAS latency
    if result["cas_latency"] is None:
        m = re.search(r"\bCL[-\s]?(\d{2})\b", t, re.IGNORECASE)
        if m:
            result["cas_latency"] = int(m.group(1))

    # Profiles
    if not result["ecc"]  and re.search(r"\bECC\b",  t, re.IGNORECASE):
        result["ecc"]  = 1
    if not result["expo"] and re.search(r"\bEXPO\b", t, re.IGNORECASE):
        result["expo"] = 1
    if not result["xmp"]  and re.search(r"\bXMP\b",  t, re.IGNORECASE):
        result["xmp"]  = 1

    # Re-derive per-stick if now computable
    if result["capacity_per_stick_gb"] is None:
        cap  = result["total_capacity_gb"]
        stks = result["sticks"]
        if cap and stks and stks > 0 and cap % stks == 0:
            result["capacity_per_stick_gb"] = cap // stks

    return result
