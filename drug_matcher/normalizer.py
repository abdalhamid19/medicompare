"""Name normalization and drug component parsing."""
import re
from dataclasses import dataclass

from rapidfuzz import fuzz

FORM_WORDS = frozenset({
    "TABLET", "TABLETS", "TAB", "TABS", "CAP", "CAPS", "CAPSULE", "CAPSULES",
    "SACHET", "SACHETS", "SACH", "AMP", "AMPS", "AMPOULE", "AMPOULES", "VIAL", "VIALS",
    "SUPP", "SUPPS", "PIECE", "PIECES", "DROPS", "DROP", "PEN", "PENS",
    "CARTRIDGE", "CARTRIDGES", "GUMMIES", "PACKETS",
    "F.C.TAB", "F.C.TABS", "F.C. TAB", "F.C. TABS", "F.C.TAB.", "F.C.TABS.",
    "E.C.TAB", "E.C.TABS", "E.C. TAB", "E.C. TABS",
    "EXT.REL.TAB", "EXT. REL. TABS", "E.R.F.C.TABS",
    "CHEW.TAB", "CHEWABLE TAB", "SUGAR COATED TAB",
    "S.G.CAPS", "S.G. CAPS", "H.G.CAPS", "H.G. CAPS",
    "ORODISSOLVABLE", "FILM", "FILMS", "LOZENGES",
})

FORM_PREFIXES = frozenset({
    "CREAM", "GEL", "OINTMENT", "OINT", "SYRUP", "SUSP", "SPRAY",
    "POWDER", "LOTION", "SOAP", "SHAMPOO", "OIL", "SERUM",
    "EMULGEL", "INJECTION", "INFUSION", "SOLUTION", "SOLN",
    "TOPICAL", "ORAL", "EYE", "NASAL", "EAR", "INTIMATE",
    "MASSAGE", "FEMININE", "CLEANSER", "WASH", "DOUCHE",
    "INHALER", "INH",
})

NOISE_WORDS = frozenset({
    "BLUE", "RED", "WHITE", "ORS", "FLAVOR", "FLAVOUR",
    "LIQUID", "FACIAL",
})
BRAND_QUALIFIERS = frozenset({"INFINITY", "SURACTIVE"})
FLAVOR_WORDS = frozenset({
    "BANANA", "ORANGE", "PINEAPPLE", "STRAWBERRY",
})
CRITICAL_MODIFIERS = frozenset({
    "PLUS", "EXTRA", "ADVANCE", "FORTE", "NIGHT", "COLD",
    "SINUS", "IMP", "IMPORTED", "D",
})

@dataclass(slots=True)
class DrugComponents:
    brand: str
    dosage_nums: tuple[str, ...]
    dosage_units: tuple[str, ...]
    qty: str
    volume: str
    weight: str
    form: str
    flavor: str
    normalized: str

_DOSAGE_RE = re.compile(
    r"(\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?(?:\s\d{3})?)"
    r"\s*(MG|MCG|I\s*U|IU|%)(?=$|\s)",
    re.IGNORECASE,
)
_WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(GM|G)\b", re.IGNORECASE)
_QTY_RE = re.compile(r"(\d+)\s*(TAB|TABS|CAP|CAPS|SACHET|SACH|AMPS|AMP|VIAL|SUPP|PIECE|DROPS|PEN|CARTRIDGE|GUMMIES|GUM|PACKETS)\b", re.IGNORECASE)
_VOL_RE = re.compile(r"(\d+)\s*ML\b", re.IGNORECASE)
_NOISE_PREFIX_RE = re.compile(r"^[+*.]+\s*(IMP|IMPORTED)?\s*", re.IGNORECASE)

def normalize(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    name = name.strip().upper()
    name = _NOISE_PREFIX_RE.sub("", name)
    name = re.sub(r"-+", " ", name)
    name = re.sub(r"[()]", " ", name)
    # Split compact drug notation before parsing: PANADOL20MG -> PANADOL 20 MG, 30TAB -> 30 TAB
    name = re.sub(r"([A-Z])(?=\d)", r"\1 ", name)
    name = re.sub(r"(?<=\d)([A-Z])", r" \1", name)
    name = re.sub(r"\s*[\\/]\s*", " / ", name)
    # Handle European decimal notation BEFORE removing dots: "1.000" IU means 1000
    name = re.sub(r'(\d)\.(\d{3})\s*(I\.?U\.?|IU|MCG|MG)', r'\1\2 \3', name)
    # Remove dots but NOT between digits that form a decimal (e.g. 0.5, 2.5)
    name = re.sub(r'\.(?!\d)', ' ', name)
    name = re.sub(r'(?<!\d)\.', ' ', name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def parse_drug(name: str) -> DrugComponents:
    if not name or not isinstance(name, str):
        return DrugComponents("", (), (), "", "", "", "", "", "")

    norm = normalize(name)

    # Dosage (MG, MCG, IU, %) - NOT GM/G (those are weight/packaging)
    d_matches = _DOSAGE_RE.findall(norm)
    dosage_nums = tuple(re.sub(r"\s+", "", m[0]) for m in d_matches)
    dosage_units = tuple(m[1] for m in d_matches)

    # Weight (GM/G) - stored separately, not as dosage
    w_matches = _WEIGHT_RE.findall(norm)
    weight = w_matches[-1][0] if w_matches else ""

    # Quantity
    q = _QTY_RE.search(norm)
    qty = q.group(1) if q else ""

    # Volume
    v = _VOL_RE.findall(norm)
    volume = v[-1] if v else ""

    # Brand: first alphabetic words before any number
    words = norm.split()
    brand_words: list[str] = []
    for w in words:
        if re.search(r"\d", w):
            break
        if (
            w in FORM_PREFIXES or w in FORM_WORDS
            or w in NOISE_WORDS or w in BRAND_QUALIFIERS
        ):
            break
        brand_words.append(w)
    brand = "".join(brand_words)
    if not brand and words and words[0] in BRAND_QUALIFIERS:
        brand = "".join(
            w for w in words[1:]
            if (
                not re.search(r"\d", w)
                and w not in FORM_PREFIXES
                and w not in FORM_WORDS
                and w not in NOISE_WORDS
                and w not in BRAND_QUALIFIERS
            )
        )

    # Form detection — use word-boundary check to avoid "OINT" matching inside "JOINT"
    form = ""
    norm_words = set(norm.split())
    for fw in FORM_PREFIXES:
        if fw in norm_words:
            form = fw
            break
    flavor = ""
    for fw in FLAVOR_WORDS:
        if fw in norm_words:
            flavor = fw
            break

    return DrugComponents(
        brand=brand,
        dosage_nums=dosage_nums,
        dosage_units=dosage_units,
        qty=qty,
        volume=volume,
        weight=weight,
        form=form,
        flavor=flavor,
        normalized=norm,
    )

def components_match(
    d: DrugComponents,
    m: DrugComponents,
    brand_prefix_min: int = 4,
) -> tuple[bool, str]:
    """Verify two drug components represent the same product. Returns (is_match, reason)."""
    # Brand check
    d_clean = re.sub(r"[^A-Z0-9]", "", d.brand)
    m_clean = re.sub(r"[^A-Z0-9]", "", m.brand)

    for modifier in CRITICAL_MODIFIERS:
        if (modifier in d.normalized.split()) != (modifier in m.normalized.split()):
            return False, "different_modifier"

    if d_clean and m_clean:
        shorter = min(len(d_clean), len(m_clean))
        prefix_len = min(
            len(d_clean), len(m_clean),
            max(brand_prefix_min, int(shorter * 0.75)),
        )
        prefix_len = min(prefix_len, len(d_clean), len(m_clean))
        if prefix_len > 0 and d_clean[:prefix_len] != m_clean[:prefix_len]:
            if (
                d_clean not in m_clean and m_clean not in d_clean
                and fuzz.ratio(d_clean, m_clean) < 86
            ):
                return False, "different_brand"
        if d_clean != m_clean and d_clean not in m_clean and m_clean not in d_clean:
            if fuzz.ratio(d_clean, m_clean) < 86:
                return False, "different_brand"
        if d_clean != m_clean and (d_clean in m_clean or m_clean in d_clean):
            shorter = min(len(d_clean), len(m_clean))
            longer = max(len(d_clean), len(m_clean))
            if longer - shorter > 2 and fuzz.ratio(d_clean, m_clean) < 86:
                return False, "different_brand"

    # Dosage check
    if d.dosage_nums and m.dosage_nums:
        for i in range(min(len(d.dosage_nums), len(m.dosage_nums))):
            if d.dosage_nums[i] != m.dosage_nums[i]:
                return False, "different_dosage"

    # Quantity check
    if d.qty and m.qty and d.qty != m.qty:
        return False, "different_quantity"

    # Volume check
    if d.volume and m.volume and d.volume != m.volume:
        return False, "different_volume"

    # Weight check
    if d.weight and m.weight and d.weight != m.weight:
        return False, "different_weight"

    if d.flavor and m.flavor and d.flavor != m.flavor:
        return False, "different_flavor"

    return True, "ok"
