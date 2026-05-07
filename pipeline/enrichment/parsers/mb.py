import re

from enrichment.fetch import fetch_spec_text

BRANDS = ["ASUS", "Gigabyte", "MSI", "ASRock", "Biostar", "NZXT", "Colorful", "Supermicro"]


def _clean(s: str) -> str:
    return (s or "").replace("\xa0", " ").replace("­", " ").strip()


def _brand_from_title(title: str) -> str | None:
    for b in BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", title, re.IGNORECASE):
            return b
    return None


def _model_from_title(title: str, brand: str | None) -> str | None:
    if not title:
        return None
    t = re.sub(r"^\s*(MB|Motherboard|[МмPp]лоч[ае]|[Мм]атична\s+плоча)\s+", "", title.strip(), flags=re.IGNORECASE)
    if brand:
        t = re.sub(rf"^\s*{re.escape(brand)}\s+", "", t, flags=re.IGNORECASE)
    stop = re.split(
        r"\s+(?:LGA|AM[45]|DDR[45]|WIFI|Wi-?Fi|USB|PCIe|SATA|M\.2|ATX|mATX|Micro|Mini)\b",
        t, maxsplit=1, flags=re.IGNORECASE,
    )
    base = re.sub(r"\b(LGA\s*\d+|AM[45])\b", "", stop[0], flags=re.IGNORECASE).strip()
    return base if len(base) >= 4 else None


def _infer_from_chipset(chipset: str) -> tuple[str | None, str | None]:
    """Return (socket, memory_type) inferred from chipset model number."""
    m = re.search(r"([ABHXZW])(\d{3})", chipset.upper())
    if not m:
        return None, None
    letter, num = m.group(1), int(m.group(2))
    # Z, H, W — always Intel
    if letter in ("Z", "H", "W"):
        if num <= 590:
            return "LGA1200", "DDR4"
        if num <= 790:
            return "LGA1700", None   # DDR4 or DDR5 depending on board
        return "LGA1851", "DDR5"
    # A, X — always AMD
    if letter in ("A", "X"):
        return ("AM4", "DDR4") if num < 600 else ("AM5", "DDR5")
    # B — Intel ends in 60 (B360/460/560/660/760/860), AMD ends in 50 (B350/450/550/650/850)
    if letter == "B":
        if num % 100 == 60:          # Intel B-series
            if num <= 560:
                return "LGA1200", "DDR4"
            if num <= 760:
                return "LGA1700", None
            return "LGA1851", "DDR5"
        return ("AM4", "DDR4") if num < 600 else ("AM5", "DDR5")
    return None, None


NON_MB_WORDS = ["напојување", "napojuvanje", "riser cable", "3d printer", "3d печатач"]


def parse(title_hint: str, url: str | None = None) -> dict | None:
    title = _clean(title_hint)
    if any(w in title.lower() for w in NON_MB_WORDS):
        return None
    raw_text = fetch_spec_text(url) if url else None
    text = _clean(raw_text) if raw_text else None

    mb = {
        "mb_model": None, "brand": None, "chipset": None, "socket": None,
        "form_factor": None, "memory_type": None, "memory_slots": None,
        "max_memory_gb": None, "pcie_version": None,
    }

    brand = _brand_from_title(title)
    mb["brand"] = brand
    model = _model_from_title(title, brand)
    if brand and model and not model.lower().startswith(brand.lower()):
        mb["mb_model"] = f"{brand} {model}".strip()
    else:
        mb["mb_model"] = model

    m = re.search(r"\b([ABHXZW]\d{3}E?)(?!\d)", title, re.IGNORECASE)
    if m:
        mb["chipset"] = m.group(1).upper()

    # --- Socket ---
    socket = None
    if text:
        m = re.search(
            r"\b(CPU Socket|Socket)\s*:\s*(?:AMD\s+Socket\s+)?(AM4|AM5|LGA\s*\d{4})\b",
            text, re.IGNORECASE,
        )
        if m:
            socket = m.group(2).replace(" ", "").upper()
        if not socket:
            m = re.search(r"\bFC?LGA\s*(\d{4})\b", text, re.IGNORECASE)
            if m:
                socket = f"LGA{m.group(1)}"
        if not socket:
            m = re.search(r"\b(AM[45]|LGA\s*\d{4})\b", text, re.IGNORECASE)
            if m:
                socket = m.group(1).replace(" ", "").upper()
    if not socket:
        m = re.search(r"\b(AM[45]|LGA\s*\d{4}|s?TR\d)\b", title, re.IGNORECASE)
        if m:
            socket = m.group(1).replace(" ", "").upper()
    # "Socket 1700" / "Socket 1851" etc. → LGA
    if not socket:
        m = re.search(r"\bSocket\s+(\d{4})\b", title, re.IGNORECASE)
        if m:
            socket = f"LGA{m.group(1)}"
    if not socket and mb["chipset"]:
        socket, _ = _infer_from_chipset(mb["chipset"])
    mb["socket"] = socket

    # --- Memory type ---
    memory_type = None
    if text:
        if re.search(r"\bDDR5\b", text, re.IGNORECASE):
            memory_type = "DDR5"
        elif re.search(r"\bDDR4\b", text, re.IGNORECASE):
            memory_type = "DDR4"
    if not memory_type:
        m = re.search(r"\b(DDR[45])\b", title, re.IGNORECASE)
        if m:
            memory_type = m.group(1).upper()
    # Model suffix D4/D5 (e.g. "B760-PLUS D4", "H610MH D5")
    if not memory_type:
        m = re.search(r"\bD([45])\b", title)
        if m:
            memory_type = f"DDR{m.group(1)}"
    if not memory_type and mb["chipset"]:
        _, memory_type = _infer_from_chipset(mb["chipset"])
    mb["memory_type"] = memory_type

    # --- Form factor ---
    ff = None
    if text:
        m = re.search(r"\bForm Factor\s*:\s*([A-Za-z -]+?)\s*Form Factor\b", text, re.IGNORECASE)
        if m:
            raw = m.group(1).strip().lower()
            if "micro" in raw and "atx" in raw:
                ff = "Micro-ATX"
            elif "mini" in raw and "itx" in raw:
                ff = "Mini-ITX"
            elif "atx" in raw:
                ff = "ATX"
        if not ff:
            if re.search(r"\bMicro\s*ATX\b", text, re.IGNORECASE):
                ff = "Micro-ATX"
            elif re.search(r"\bMini\s*ITX\b", text, re.IGNORECASE):
                ff = "Mini-ITX"
            elif re.search(r"\bATX\b", text, re.IGNORECASE):
                ff = "ATX"
    if not ff:
        if re.search(r"\b(Micro\s*ATX|mATX)\b", title, re.IGNORECASE):
            ff = "Micro-ATX"
        elif re.search(r"\b(Mini\s*ITX)\b", title, re.IGNORECASE):
            ff = "Mini-ITX"
        elif re.search(r"\bATX\b", title, re.IGNORECASE):
            ff = "ATX"
    mb["form_factor"] = ff

    # --- Memory slots, max memory, PCIe (spec page only) ---
    if text:
        m = re.search(r"\b(\d+)\s*x\s*DDR[45]\s*DIMM", text, re.IGNORECASE)
        if m:
            mb["memory_slots"] = int(m.group(1))

        m = re.search(r"\bup to\s*(\d+)\s*GB\b", text, re.IGNORECASE)
        if m:
            mb["max_memory_gb"] = int(m.group(1))

        versions = set()
        for m in re.finditer(
            r"\bPCI(?:e| Express(?:®)?)(?:\s+Revision)?\s*[:®]?\s*(?:Gen\s*)?([345](?:\.\d)?)\b",
            text, re.IGNORECASE,
        ):
            versions.add(m.group(1))
        for m in re.finditer(r"\bPCIe(?:®)?\s*([345](?:\.\d)?)\b", text, re.IGNORECASE):
            versions.add(m.group(1))
        if versions:
            mb["pcie_version"] = sorted(
                versions,
                key=lambda v: tuple(int(x) for x in (v + ".0").split(".")[:2]),
                reverse=True,
            )[0]

    # PCIe version from title as fallback
    if not mb["pcie_version"]:
        m = re.search(r"\bPCIe\s*([345](?:\.\d)?)\b", title, re.IGNORECASE)
        if m:
            mb["pcie_version"] = m.group(1)

    # Require at least socket and memory_type (from any source)
    if not mb["socket"] or not mb["memory_type"]:
        return None

    return mb
