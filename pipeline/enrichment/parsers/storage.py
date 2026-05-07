import re

from enrichment.fetch import fetch_spec_text

KNOWN_BRANDS = [
    "Samsung", "Seagate", "Western Digital", "WD", "Toshiba",
    "Kingston", "Crucial", "ADATA", "Adata", "SanDisk",
    "Lexar", "TeamGroup", "PNY", "Intel", "Netac", "Verbatim",
]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse(title: str, url: str | None = None) -> dict | None:
    t = _norm(title)

    if re.search(r"\b(cooler|adapter|enclosure|case)\b", t, re.IGNORECASE):
        return None
    if re.search(
        r"[Кк]уќиш|riser|[Чч]итач|card\s*reader|[Фф]леш|USB\s*стик|NAS\s*сервер|докинг",
        t, re.IGNORECASE,
    ):
        return None

    storage_type = None
    if re.search(r"\bSSD\b|\bССД\b", t, re.IGNORECASE):
        storage_type = "SSD"
    elif re.search(
        r"\bHDD\b|[Хх]ард\s+[Дд]иск|[Тт]врд(?:[ао]|ен|и)?\s+[Дд]иск|\bHard\s+[Dd]isk\b", t
    ):
        storage_type = "HDD"
    if storage_type is None:
        return None

    capacity_gb = None
    m = re.search(r"\b(\d+)\s*TB\b", t, re.IGNORECASE)
    if m:
        capacity_gb = int(m.group(1)) * 1000
    else:
        m = re.search(r"\b(\d+)\s*GB\b", t, re.IGNORECASE)
        if m:
            capacity_gb = int(m.group(1))

    form_factor = None
    if re.search(r"\bM\.2\b", t, re.IGNORECASE):
        form_factor = "M.2"
    elif re.search(r'2\.5"', t):
        form_factor = '2.5"'
    elif re.search(r'3\.5"', t):
        form_factor = '3.5"'

    interface = None
    if re.search(r"\bNVMe\b", t, re.IGNORECASE):
        interface = "NVMe"
    elif re.search(r"\bSATA[-\s]?(?:3|III)\b|\bSATA3\b", t, re.IGNORECASE):
        interface = "SATA3"
    if interface is None:
        if storage_type == "SSD" and form_factor == '2.5"':
            interface = "SATA3"
        elif storage_type == "HDD":
            interface = "SATA3"

    pcie_version = None
    m = re.search(r"\bPCIe\s*([345]\.0)\b", t, re.IGNORECASE)
    if m:
        pcie_version = m.group(1)

    rpm = None
    m = re.search(r"\b(\d{4,5})\s*rpm\b", t, re.IGNORECASE)
    if m:
        rpm = int(m.group(1))

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
                r"\b(PCIe|SATA|SSD|HDD|\d+TB|\d+GB|\d+rpm|AES|NAS)\b",
                after[1], maxsplit=1, flags=re.IGNORECASE,
            )[0]
            series = _norm(s) or None

    result = {
        "type": storage_type, "brand": brand, "series": series,
        "capacity_gb": capacity_gb, "form_factor": form_factor,
        "interface": interface, "pcie_version": pcie_version, "rpm": rpm,
    }

    # Enrich with spec page data when URL is available
    if url:
        try:
            text = fetch_spec_text(url)
            if text:
                result = _enrich_from_text(result, text)
        except Exception:
            pass

    return result


def _enrich_from_text(result: dict, text: str) -> dict:
    """Override/supplement title-parsed values with data from the spec page."""
    t = text

    # Capacity — spec page is more precise
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*TB\b", t, re.IGNORECASE)
    if m:
        result["capacity_gb"] = int(float(m.group(1)) * 1000)
    elif result["capacity_gb"] is None:
        m = re.search(r"\b(\d+)\s*GB\b", t, re.IGNORECASE)
        if m:
            result["capacity_gb"] = int(m.group(1))

    # Form factor
    if result["form_factor"] is None:
        if re.search(r"\bM\.2\b|\bM2\b", t, re.IGNORECASE):
            result["form_factor"] = "M.2"
        elif re.search(r'2\.5["\s]|2\.5\s*inch', t, re.IGNORECASE):
            result["form_factor"] = '2.5"'
        elif re.search(r'3\.5["\s]|3\.5\s*inch', t, re.IGNORECASE):
            result["form_factor"] = '3.5"'

    # Interface
    if result["interface"] is None:
        if re.search(r"\bNVMe\b", t, re.IGNORECASE):
            result["interface"] = "NVMe"
        elif re.search(r"\bSATA\s*(?:3|III|6G)\b|\bSATA3\b|\bSATA6Gb\b", t, re.IGNORECASE):
            result["interface"] = "SATA3"
        elif re.search(r"\bSATA\b", t, re.IGNORECASE):
            result["interface"] = "SATA3"

    # PCIe generation
    if result["pcie_version"] is None:
        m = re.search(r"\bPCIe\s*(?:Gen\s*)?([345])(?:\.\d)?\b", t, re.IGNORECASE)
        if m:
            result["pcie_version"] = f"{m.group(1)}.0"
        else:
            m = re.search(r"\bGen(?:eration)?\s*([345])\b", t, re.IGNORECASE)
            if m:
                result["pcie_version"] = f"{m.group(1)}.0"

    # RPM for spinning disks
    if result["rpm"] is None:
        m = re.search(r"\b(\d{4,5})\s*RPM\b", t, re.IGNORECASE)
        if m:
            result["rpm"] = int(m.group(1))

    # Inference from combined form_factor + type
    if result["interface"] is None:
        if result["type"] == "SSD" and result["form_factor"] == '2.5"':
            result["interface"] = "SATA3"
        elif result["type"] == "HDD":
            result["interface"] = "SATA3"
        elif result["type"] == "SSD" and result["form_factor"] == "M.2":
            result["interface"] = "NVMe"

    return result
