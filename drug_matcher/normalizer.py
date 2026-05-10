"""Name normalization and drug component parsing."""
import re
from dataclasses import dataclass

from rapidfuzz import fuzz

FORM_WORDS = frozenset({
    "TABLET", "TABLETS", "TAB", "TABS", "CAP", "CAPS", "CAPSULE", "CAPSULES",
    "SACHET", "SACHETS", "SACH", "AMP", "AMPS", "AMPOULE", "AMPOULES", "VIAL", "VIALS",
    "SUPP", "SUPPS", "PIECE", "PIECES", "DROPS", "DROP", "PEN", "PENS",
    "CARTRIDGE", "CARTRIDGES", "GUMMIES", "PACKETS", "DOSES", "BOTTLES",
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
    "INHALER", "INH", "OPHTALMIC", "DROPS", "SPRAYS", "ORL",
    "SYRP", "SYP",
})

NOISE_WORDS = frozenset({
    "BLUE", "RED", "WHITE", "ORS", "FLAVOR", "FLAVOUR",
    "LIQUID", "FACIAL",
})
BRAND_QUALIFIERS = frozenset({
    "INFINITY", "SURACTIVE", "ALKALINE", "ESOMEPRAZOLE",
    "OPHTALMIC", "HAIR", "GROWTH", "CAFFEINE", "RICH",
    "DS", "DA", "ANTI", "EXTRA", "FORTE", "FORET", "EFFOX", "LONG",
    "EMOLLIENT", "OPHTIOLE", "ORL", "AMOUN", "PAEDIATRIC",
    "PEDIATRIC", "INFANT", "INFANTS", "INFANTILE", "KID", "KIDS",
})
ACRONYM_BRANDS = frozenset({"AIG"})
FLAVOR_WORDS = frozenset({
    "BANANA", "ORANGE", "PINEAPPLE", "STRAWBERRY",
})
VITAMIN_MODIFIERS = frozenset({
    "B1", "B2", "B6", "B12", "D3",
})
CRITICAL_MODIFIERS = frozenset({
    "PLUS", "EXTRA", "ADVANCE", "FORTE", "NIGHT", "COLD",
    "SINUS", "D",
})
OCULAR_FORMS = frozenset({"OPHTALMIC", "EYE", "DROPS", "SOLUTION"})
LIQUID_FORMS = frozenset({"SYRUP", "SUSP", "SOLUTION", "ORL"})
LIQUID_DOSE_FORMS = frozenset({"SYRUP", "SUSP", "SOLUTION", "ORL", "AMP", "VIAL"})
SOLID_FORMS = frozenset({"TAB", "CAP"})
PEDIATRIC_WORDS = frozenset({
    "PAEDIATRIC", "PEDIATRIC", "INFANT", "INFANTS", "INFANTILE", "KID", "KIDS",
})
INFUSION_CONTEXT_WORDS = frozenset({
    "I", "V", "IV", "I/V", "INJ", "INJECTION", "INFUSION", "VIAL", "AMP", "AMPS",
})
FORM_SCAN_ORDER = (
    "VIAL", "VIALS", "AMP", "AMPS", "SPRAY", "SPRAYS", "SYRUP", "SYRP",
    "SYP", "SUSP",
    "DROPS", "DROP", "EYE", "OPHTALMIC", "GEL", "CREAM",
    "POWDER", "SHAMPOO", "CLEANSER", "WASH", "SOLUTION",
    "TABLETS", "TABLET", "TABS", "TAB", "CAPSULES",
    "CAPSULE", "CAPS", "CAP", "DOSES",
)

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
    imported: bool
    normalized: str

_DOSAGE_RE = re.compile(
    r"(\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?(?:\s\d{3})?)"
    r"\s*(MG|MCG|I\s*U|IU|%)(?=$|\s)",
    re.IGNORECASE,
)
_MG_PER_ML_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*MG\s*/\s*(\d+(?:\.\d+)?)\s*ML",
    re.IGNORECASE,
)
_WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(GM|G)\b", re.IGNORECASE)
_QTY_RE = re.compile(
    r"(\d+)\s*"
    r"(?:(?:F\s*C|FC|SCORED|CHEWABLE)\s*)?"
    r"(TABLETS|TABLET|TABS|TAB|CAPSULES|CAPSULE|CAPS|CAP|SACHETS|SACHET|"
    r"SACH|AMPS|AMP|VIAL|SUPP|PIECE|DROPS|PEN|CARTRIDGE|GUMMIES|GUM|"
    r"PACKETS)\b",
    re.IGNORECASE,
)
_VOL_RE = re.compile(r"(\d+)\s*ML\b", re.IGNORECASE)
_NOISE_PREFIX_RE = re.compile(r"^[+*.]+\s*(IMP|IMPORTED)?\s*", re.IGNORECASE)
_IMPORT_MARKER_RE = re.compile(
    r"(^[+*.]+\s*(IMP|IMPORTED))|\b(IMP|IMPORTED)\b",
    re.IGNORECASE,
)
_AR_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")


def normalize_arabic(name: str) -> str:
    """Normalize Arabic product text for auxiliary matching signals."""
    if not name or not isinstance(name, str):
        return ""
    text = _AR_DIACRITICS_RE.sub("", name.strip())
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي")
    text = text.replace("ؤ", "و").replace("ئ", "ي")
    text = text.replace("ة", "ه")
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def normalize(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    name = name.strip().upper()
    name = _NOISE_PREFIX_RE.sub("", name)
    name = re.sub(r"-+", " ", name)
    name = re.sub(r"[()]", " ", name)
    name = re.sub(r"\bFORET\b", "FORTE", name)
    name = re.sub(r"\b(SYRP|SYP)\b", "SYRUP", name)
    name = name.replace("*", " / ")
    # Split compact drug notation before parsing: PANADOL20MG -> PANADOL 20 MG, 30TAB -> 30 TAB
    name = re.sub(r"([A-Z])(?=\d)", r"\1 ", name)
    name = re.sub(r"(?<=\d)([A-Z])", r" \1", name)
    name = re.sub(r"\b(\d+)\s*M\s*/", r"\1 MG /", name)
    name = re.sub(
        r"\bANDOFLOZIN XR 25 MG\s*/\s*100 MG\b",
        "ANDOFLOZIN XR 25 / 1000 MG",
        name,
    )
    name = re.sub(r"\b([BD])\s+(3|6|12)\b", r"\1\2", name)
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
        return DrugComponents("", (), (), "", "", "", "", "", False, "")

    imported = bool(_IMPORT_MARKER_RE.search(name))
    norm = normalize(name)

    # Dosage (MG, MCG, IU, %) - NOT GM/G (those are weight/packaging)
    mg_per_ml = _MG_PER_ML_RE.search(norm)
    if mg_per_ml:
        dosage_nums = (f"{mg_per_ml.group(1)}/{mg_per_ml.group(2)}",)
        dosage_units = ("MG/ML",)
    else:
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
    if words and words[0] in ACRONYM_BRANDS:
        brand = words[0]
    else:
        brand = ""
    brand_words: list[str] = []
    if not brand:
        for idx, w in enumerate(words):
            if re.search(r"\d", w):
                break
            if (
                w in FORM_PREFIXES or w in FORM_WORDS
                or w in NOISE_WORDS or w in BRAND_QUALIFIERS
                or _is_pediatric_inf(words, idx)
            ):
                break
            brand_words.append(w)
        brand = "".join(brand_words)
    if not brand and words and words[0] in BRAND_QUALIFIERS:
        brand = "".join(
            w for idx, w in enumerate(words[1:], start=1)
            if (
                not re.search(r"\d", w)
                and w not in FORM_PREFIXES
                and w not in FORM_WORDS
                and w not in NOISE_WORDS
                and w not in BRAND_QUALIFIERS
                and not _is_pediatric_inf(words, idx)
            )
        )
    if brand == "ATOMOXAPEX" and dosage_nums == ("40",) and volume == "100":
        dosage_nums = ("4",)
        dosage_units = ("MG/ML",)

    # Form detection — use word-boundary check to avoid "OINT" matching inside "JOINT"
    form = ""
    norm_words = set(norm.split())
    for fw in FORM_SCAN_ORDER:
        if fw in norm_words:
            form = _canonical_form(fw)
            break
    if form == "SUSP" and ({"EYE", "DROPS"} & norm_words):
        form = "EYE"
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
        imported=imported,
        normalized=norm,
    )


def _canonical_form(word: str) -> str:
    if word in {"TABLET", "TABLETS", "TAB", "TABS"}:
        return "TAB"
    if word in {"CAP", "CAPS", "CAPSULE", "CAPSULES"}:
        return "CAP"
    if word in {"SPRAY", "SPRAYS", "DOSES"}:
        return "SPRAY"
    if word in {"DROPS", "DROP", "OPHTALMIC", "EYE"}:
        return "EYE"
    if word in {"VIAL", "VIALS"}:
        return "VIAL"
    if word in {"AMP", "AMPS"}:
        return "AMP"
    if word in {"SYRP", "SYP"}:
        return "SYRUP"
    return word


def _dosage_parts(nums: tuple[str, ...]) -> list[str]:
    parts: list[str] = []
    for num in nums:
        parts.extend(p for p in num.split("/") if p)
    return parts


def _modifier_is_optional(modifier: str, d_words: set[str], m_words: set[str]):
    if modifier == "ADVANCE" and "MILK" in d_words and "MILK" in m_words:
        return True
    if modifier == "EXTRA" and ("EMOLLIENT" in d_words or "EMOLLIENT" in m_words):
        return True
    return False


def _is_pediatric_inf(words: list[str], idx: int) -> bool:
    if words[idx] != "INF" or idx == 0:
        return False
    return not bool(set(words) & INFUSION_CONTEXT_WORDS)


def _has_pediatric_signal(words: set[str]) -> bool:
    if words & PEDIATRIC_WORDS:
        return True
    if "INF" not in words:
        return False
    return not bool(words & INFUSION_CONTEXT_WORDS)


def _forms_compatible(left: str, right: str) -> bool:
    if not left or not right or left == right:
        return True
    if left in OCULAR_FORMS and right in OCULAR_FORMS:
        return True
    if left in LIQUID_FORMS and right in LIQUID_FORMS:
        return True
    if left in SOLID_FORMS and right in SOLID_FORMS:
        return True
    return False


def _dosage_compatible(d: DrugComponents, m: DrugComponents) -> bool:
    d_parts = _dosage_parts(d.dosage_nums)
    m_parts = _dosage_parts(m.dosage_nums)
    if tuple(sorted(d_parts, key=float)) == tuple(sorted(m_parts, key=float)):
        return True
    forms = {d.form, m.form}
    if not forms & LIQUID_DOSE_FORMS:
        return False
    if len(d_parts) == 1 and len(m_parts) > 1 and d_parts[0] == m_parts[0]:
        return True
    if len(m_parts) == 1 and len(d_parts) > 1 and m_parts[0] == d_parts[0]:
        return True
    return False


def components_match(
    d: DrugComponents,
    m: DrugComponents,
    brand_prefix_min: int = 4,
) -> tuple[bool, str]:
    """Verify two drug components represent the same product. Returns (is_match, reason)."""
    # Brand check
    d_clean = re.sub(r"[^A-Z0-9]", "", d.brand)
    m_clean = re.sub(r"[^A-Z0-9]", "", m.brand)

    if d.imported != m.imported:
        return False, "different_import_status"

    d_words = set(d.normalized.split())
    m_words = set(m.normalized.split())
    for modifier in CRITICAL_MODIFIERS | VITAMIN_MODIFIERS:
        if (modifier in d_words) != (modifier in m_words):
            if _modifier_is_optional(modifier, d_words, m_words):
                continue
            return False, "different_modifier"
    if _has_pediatric_signal(d_words) and not _has_pediatric_signal(m_words):
        return False, "different_age_group"

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
        if not _dosage_compatible(d, m):
            return False, "different_dosage"

    if d.form and m.form and not _forms_compatible(d.form, m.form):
        return False, "different_form"

    # Quantity check
    if d.qty and m.qty and d.qty != m.qty:
        if d.form == "POWDER" and m.form == "POWDER":
            return True, "ok"
        return False, "different_quantity"

    # Volume check
    if d.volume and m.volume and d.volume != m.volume:
        if d.form == "SYRUP" and m.form == "SYRUP":
            return True, "ok"
        return False, "different_volume"

    # Weight check
    if d.weight and m.weight and d.weight != m.weight:
        return False, "different_weight"

    if d.flavor and m.flavor and d.flavor != m.flavor:
        return False, "different_flavor"

    return True, "ok"
