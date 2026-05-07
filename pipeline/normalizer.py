"""
normalizer.py — extract a short, store-independent model key from a product title.

Used to deduplicate the same physical product sold under slightly different
titles across stores.  Returns None when extraction is not confident enough.
"""
import re


# ── Pre-processing ────────────────────────────────────────────────────────────

# Translate known Cyrillic product words to Latin before stripping the rest
_CYR_REPLACE = [
    # CPU brands / product names
    (re.compile(r'\bИнтел\b',   re.IGNORECASE), 'Intel'),
    (re.compile(r'\bАМД\b',     re.IGNORECASE), 'AMD'),
    (re.compile(r'\bРајзен\b',  re.IGNORECASE), 'Ryzen'),
    (re.compile(r'\bРайзен\b',  re.IGNORECASE), 'Ryzen'),
    (re.compile(r'Ra[јj][зz][eе][nн]', re.IGNORECASE), 'Ryzen'),  # mixed Latin+Cyrillic spelling
    (re.compile(r'\bКор\b',     re.IGNORECASE), 'Core'),
    (re.compile(r'\bУлтра\b',   re.IGNORECASE), 'Ultra'),
    (re.compile(r'\bПро\b',     re.IGNORECASE), 'Pro'),
    # Storage brands / product names
    (re.compile(r'\bСамсунг\b', re.IGNORECASE), 'Samsung'),
    (re.compile(r'\bЕВО\b',     re.IGNORECASE), 'EVO'),
    (re.compile(r'\bПлус\b',    re.IGNORECASE), 'Plus'),
    (re.compile(r'\bМакс\b',    re.IGNORECASE), 'Max'),
    # RAM — memory type, speed unit, profiles, brands, series
    (re.compile(r'ДДР'),                         'DDR'),   # "ДДР5" → "DDR5"
    (re.compile(r'МГц'),                         'MHz'),   # speed unit
    (re.compile(r'ЕКСПО',  re.IGNORECASE),        'EXPO'),
    (re.compile(r'\bКингстон\b', re.IGNORECASE), 'Kingston'),
    (re.compile(r'\bКорсаир\b',  re.IGNORECASE), 'Corsair'),
    (re.compile(r'\bФЈУРИ\b',   re.IGNORECASE), 'Fury'),
    (re.compile(r'\bБист\b',     re.IGNORECASE), 'Beast'),
    (re.compile(r'\bВенџенс\b',  re.IGNORECASE), 'Vengeance'),
    (re.compile(r'\bТрајдент\b', re.IGNORECASE), 'Trident'),
]

_CYRILLIC = re.compile(r'[Ѐ-ӿ]+')

# Leading non-brand text that adds no model info
_LEAD_NOISE = re.compile(
    r'^(?:'
    r'\[.*?\]\s*'                                          # [OUTLET], [SALE], etc.
    r'|Disk\s+i\s+jashtëm\s*(?:HDD|SSD)?\s*'             # Albanian: external disk
    r'|Hard\s+disk\s+i\s+jashtëm\s*(?:HDD|SSD)?\s*'
    r'|Pll?ak[ëea]+\s+[Aa]m[ëe]\s*'                      # Albanian: motherboard
    r'|Pll?at[ae]\s+p[ëe]r\s*'
    r'|Plo[čc]a\s+'                                       # Serbian: "board"
    r'|RAM\s+(?:DIMM|SO-DIMM)\s+'                         # RAM type prefix
    r'|(?:Procesor|Processor|Desktop\s+Processor)\s+'     # Latin language prefixes
    r'|(?:MB|CPU|GPU)\s+'                                  # store category prefixes (Anhoch)
    r'|(?:SSD|HDD|M\.2|Portable|Disk)\s+'                 # bare type / generic word
    r')',
    re.IGNORECASE,
)


def _preprocess(t: str) -> str:
    t = re.sub(r'[™®©]', '', t)        # strip trademark/copyright symbols
    for pat, rep in _CYR_REPLACE:
        t = pat.sub(rep, t)
    t = _CYRILLIC.sub(' ', t)          # drop remaining Cyrillic words
    t = _LEAD_NOISE.sub('', t).strip()
    t = re.sub(r'^[A-Z]\s+', '', t, flags=re.IGNORECASE)  # lone letter left after Cyrillic strip
    return re.sub(r'\s{2,}', ' ', t).strip()


# ── Public entry point ────────────────────────────────────────────────────────

def extract_model_key(title: str, category: str) -> str | None:
    cat = (category or "").lower().strip()
    t = _preprocess(title or "")
    if not t:
        return None
    if cat == "cpu":
        return _cpu_key(t)
    if cat == "gpu":
        return _gpu_key(t)
    if cat in ("ram", "memory"):
        return _ram_key(t)
    if cat == "mb":
        return _mb_key(t)
    if cat == "storage":
        return _storage_key(t)
    return None


# ── CPU ──────────────────────────────────────────────────────────────────────

def _cpu_key(t: str) -> str | None:
    # Intel Core Ultra (e.g. "Core Ultra 9 285K")
    m = re.search(r'\b(Core\s+Ultra\s+\d+\s+\d{3,4}[A-Z0-9]*)\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1))

    # Intel i3/i5/i7/i9 (e.g. "i5-13600K", "i9 14900KS" — dash or space separator)
    m = re.search(r'\b(i[3579][\s-]\d{4,5}[A-Z0-9]*)\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s', '-', m.group(1)).upper()   # normalise space → dash

    # AMD Ryzen — consumer (Ryzen 5/7/9 NNNN), PRO variants, Threadripper/Threadripper PRO
    m = re.search(
        r'\b(Ryzen\s+(?:Threadripper\s+(?:PRO\s+)?|\d\s+(?:Pro\s+)?)\d{4}[A-Z0-9]*)\b',
        t, re.IGNORECASE,
    )
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    # AMD Athlon
    m = re.search(
        r'\b(Athlon\s+(?:Gold\s+|Silver\s+|Bronze\s+)?\d{4}[A-Z0-9]*)\b',
        t, re.IGNORECASE,
    )
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    # Intel Celeron / Pentium G-series (e.g. "Celeron G5905", "Pentium G6405", "G1830")
    m = re.search(r'\b((?:(?:Celeron|Pentium)\s+)?G\d{4,5}[A-Z0-9]*)\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    return None


# ── GPU ──────────────────────────────────────────────────────────────────────

def _norm_gpu(raw: str) -> str:
    """Normalize a raw GPU token to a canonical spaced uppercase key."""
    k = raw.upper().strip()
    k = re.sub(r'(RTX|GTX|GT|RX)(\d)', r'\1 \2', k)       # brand + number space
    k = re.sub(r'(\d{3,4})\s*TI\s*S(?:UPER)?\b', r'\1 TI SUPER', k)
    k = re.sub(r'(\d{3,4})\s*TI\b', r'\1 TI', k)
    k = re.sub(r'(\d{3,4})\s*S(?:UPER)?\b', r'\1 SUPER', k)
    k = re.sub(r'(\d{3,4})\s*XTX\b', r'\1 XTX', k)
    k = re.sub(r'(\d{3,4})\s*XT\b', r'\1 XT', k)
    k = re.sub(r'(\d{3,4})\s*GRE\b', r'\1 GRE', k)
    return re.sub(r'\s+', ' ', k).strip()


def _gpu_key(t: str) -> str | None:
    # NVIDIA RTX / GTX / GT — handles spaced ("RTX 4060 Ti") and embedded ("RTX4060TI")
    m = re.search(
        r'\b((?:RTX|GTX|GT)\s*\d{3,4}(?:\s*(?:Ti\s+SUPER|Ti\s*S\b|Ti|SUPER|S\b|GRE))?)\b',
        t, re.IGNORECASE,
    )
    if m:
        return _norm_gpu(m.group(1))

    # NVIDIA RTX Pro workstation (Blackwell Pro line)
    m = re.search(r'\b(RTX\s+PRO\s+\d{4}(?:\s+Max-Q)?)\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    # NVIDIA A-series workstation (RTX A400, RTX A4000, Quadro RTX A4000)
    m = re.search(r'\b((?:Quadro\s+)?RTX\s+A\d{3,4})\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip()).upper()

    # NVIDIA Quadro T/P series
    m = re.search(r'\b(Quadro\s+[TP]\d{3,4})\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    # AMD RX — handles "RX 7900 XTX" and embedded "RX9070XT"
    m = re.search(
        r'\b(?:Radeon\s+)?(RX\s*\d{3,4}(?:\s*(?:XTX|XT|GRE))?)\b',
        t, re.IGNORECASE,
    )
    if m:
        return _norm_gpu(m.group(1))

    # AMD Radeon Pro / WX workstation
    m = re.search(r'\b((?:Radeon\s+Pro\s+)?W[X]?\s*\d{4})\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip()).upper()

    # Intel Arc
    m = re.search(r'\b(Arc\s+[AB]\d{3,4}(?:\s+\w+)?)\b', t, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', ' ', m.group(1).strip())

    return None


# ── RAM ──────────────────────────────────────────────────────────────────────

def _ram_key(t: str) -> str | None:
    m = re.search(r'\b(DDR[345])\b', t, re.IGNORECASE)
    if not m:
        return None
    ddr = m.group(1).upper()

    # Total capacity — take the largest GB value (e.g. "32GB 2x16GB" → 32)
    caps = [int(x) for x in re.findall(r'\b(\d+)\s*GB\b', t, re.IGNORECASE)]
    if not caps:
        return None
    cap = max(caps)

    # Speed: "6000MHz" or "DDR5-6000"
    sm = re.search(r'\b(\d{4,5})\s*(?:MHz|Mhz)\b', t)
    if not sm:
        sm = re.search(rf'{ddr}[-/](\d{{4,5}})\b', t, re.IGNORECASE)
    speed = sm.group(1) if sm else None

    if speed:
        return f"{ddr}-{speed}-{cap}GB"
    return f"{ddr}-{cap}GB"


# ── Motherboard ───────────────────────────────────────────────────────────────

_MB_STOP = re.compile(
    r'\s+(?:Wi-?Fi\b|DDR[45]\b|mATX\b|Micro-?ATX\b|Mini-?ITX\b|ATX\b|'
    r'LGA\s?\d+|AM[45]\b|USB\b|PCIe\b|SATA\b|Bluetooth\b|BT\b|Socket\b|'
    r'AMD\b|Intel\b|\()',
    re.IGNORECASE,
)


def _mb_key(t: str) -> str | None:
    # Chipset: handles mainstream (B650E-F, H610MH, A620AM, B760MX2-E),
    # workstation (TRX50, WRX90), Intel Q/W-series (Q870M-C-CSM), legacy 2-digit (H81M)
    m = re.search(
        r'\b((?:TRX|WRX|[A-Z])\d{2,3}[A-Z]{0,3}\d?(?:-[A-Z0-9]+)*)\b',
        t, re.IGNORECASE,
    )
    if not m:
        return None
    chipset = m.group(1).upper()

    after = t[m.end():]   # keep leading space — stop pattern needs it
    stop = _MB_STOP.search(after)
    suffix = after[:stop.start()] if stop else after
    # Also stop at first comma (separates board name from appended platform specs)
    comma = suffix.find(',')
    if comma >= 0:
        suffix = suffix[:comma]
    suffix = re.sub(r'\s+', ' ', suffix).strip(' -/,')
    # Drop spec-value suffixes like "96GB", "128GB" (max memory shown in some titles)
    suffix = re.sub(r'\b\d+\s*GB\b.*$', '', suffix, flags=re.IGNORECASE).strip(' -/,')

    if suffix and 2 <= len(suffix) <= 50:
        return f"{chipset} {suffix}"
    return chipset


# ── Storage ──────────────────────────────────────────────────────────────────

# Ordered by priority — longer/more-specific brand names first
_STORAGE_BRANDS = [
    "Western Digital", "Silicon Power", "SK Hynix",
    "Samsung", "SanDisk", "Seagate", "Crucial", "Kingston",
    "Micron", "Lexar", "Toshiba", "KIOXIA", "Corsair",
    "Sabrent", "PNY", "Patriot", "ADATA", "XPG",
    "Transcend", "Intenso", "Verbatim", "Goodram", "GoodRam",
    "Apacer", "TeamGroup", "AFOX", "Gigabyte", "MSI",
    "HP", "Dell", "HGST", "Fujitsu", "DGM", "Timetec",
    "WD",   # after "Western Digital" so longer match wins
]

# Remove everything from first form-factor/interface keyword onward
# (applied on the text BETWEEN brand and capacity)
_SERIES_NOISE = re.compile(
    r'\s*[,\"]?\s*(?:NVMe|M\.2|SSD|HDD|SATA|PCIe|Gen\s*\d|'
    r'Internal|External|Solid\s+State|Hard\s+Drive|'
    r'Read|Write|\d+\s*MB/?s|2\.5["\']?|3\.5["\']?|mSATA)\b.*$',
    re.IGNORECASE,
)


def _storage_key(t: str) -> str | None:
    # Capacity (prefer TB over GB when both present, e.g. "1000GB" vs "1TB")
    caps_tb = re.findall(r'\b(\d+(?:\.\d+)?)\s*TB\b', t, re.IGNORECASE)
    caps_gb = re.findall(r'\b(\d+)\s*GB?\b', t, re.IGNORECASE)

    if caps_tb:
        val = float(caps_tb[0])
        cap = f"{int(val)}TB" if val == int(val) else f"{val}TB"
    elif caps_gb:
        cap = f"{max(int(x) for x in caps_gb)}GB"
    else:
        return None

    # Find brand
    brand = None
    bm = None
    for b in _STORAGE_BRANDS:
        bm = re.search(rf'\b{re.escape(b)}\b', t, re.IGNORECASE)
        if bm:
            brand = b
            break

    if not brand:
        return cap

    # Re-find capacity match position for slicing
    cap_match = re.search(r'\b\d+(?:\.\d+)?\s*(?:TB|GB?)\b', t, re.IGNORECASE)
    if not cap_match or cap_match.start() < bm.end():
        return f"{brand} {cap}"

    between = t[bm.end():cap_match.start()].strip()
    between = _SERIES_NOISE.sub('', between)
    between = re.sub(r'[,\s]+$', '', between)   # trailing comma/space
    between = re.sub(r'\s+', ' ', between).strip(' -/,')

    if between and 2 <= len(between) <= 45:
        return f"{brand} {between} {cap}"
    return f"{brand} {cap}"
