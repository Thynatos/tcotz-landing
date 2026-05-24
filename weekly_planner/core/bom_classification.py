"""
ERP / template row classification for SAYIM-style exports and BOM seeding.

These constants map Turkish `AÇIKLAMA` categories to planner products for
future loaders; they do not change optimizer math by themselves.
"""
from __future__ import annotations

import math
from typing import Literal

# Finished / semi-finished stock rows (not raw materials)
ERP_CATEGORY_TO_PRODUCTS: dict[str, frozenset[int]] = {
    "KOVA BOBA": frozenset({1}),
    "YARIMAMUL BOBA": frozenset({2}),
    "BARDAK BOBA (CUP)": frozenset({3}),
    "TENEKE BOBA": frozenset({4}),
    "60ML BOBA": frozenset({1}),
}

# Ingredient-style categories (default product scope for BOM seed heuristics)
BUBBLE_CORE_CATEGORIES = frozenset(
    {
        "GLIKOZ",
        "KALSIYUM LAKTAT",
        "SODYUM ALJINAT IMP",
        "TOZ MALTODEKSTRIN",
    }
)

ALL_PRODUCTS = frozenset({1, 2, 3, 4})

FLAVOR_ALL_PRODUCTS_CATEGORIES = frozenset({"AROMA"})

# Fruit concentrate: match substring in category or product name
FRUIT_CONCENTRATE_SUBSTRINGS = ("KONSANTRESI", "KONSANTRE")

# Packaging heuristics (optional seeding)
DRINK_PACKAGING_SUBSTRINGS = ("BASKISIZ UST FILM", "KOLI ", "KUTU")
BUBBLE_PACKAGING_CATEGORIES = frozenset({"ETİKET", "ETIKET"})


RmBucket = Literal["base_rm", "rm4", "rm7", "rm8"]


# ---------------------------------------------------------------------------
# UI-facing RM labels
# ---------------------------------------------------------------------------
# The optimizer tracks ten distinct raw materials (RM1..RM10) but ERP stock is
# rolled up into four buckets: base_rm, rm4, rm7, rm8 (see sayim_row_rm_bucket).
# RM_LABELS is the single source of truth for displaying what each RM actually
# means in the UI (BOM grid, initial-state inputs, in-transit editor, help text).
#
# Each entry: {
#   "short":        Short descriptor shown inline (e.g. column tooltips).
#   "description":  One-line plain-language definition (ERP examples).
#   "bucket":       Which initial-state ERP stock bucket this RM draws from.
# }
RM_LABELS: dict[int, dict[str, str]] = {
    1: {
        "short": "Bubble core ingredient A",
        "description": "Bulk bubble-core ingredient (e.g. GLIKOZ / glucose).",
        "bucket": "base_rm",
    },
    2: {
        "short": "Bubble core ingredient B",
        "description": "Bulk bubble-core ingredient (e.g. KALSIYUM LAKTAT / calcium lactate).",
        "bucket": "base_rm",
    },
    3: {
        "short": "Bubble core ingredient C",
        "description": "Bulk bubble-core ingredient (e.g. SODYUM ALJINAT / sodium alginate, MALTODEKSTRIN).",
        "bucket": "base_rm",
    },
    4: {
        "short": "Bubble packaging (KOVA-KAPAK, ETIKET)",
        "description": "Bucket / bottle packaging and labels for P1/P3 (KOVA-KAPAK, GOVDE ETIKET).",
        "bucket": "rm4",
    },
    5: {
        "short": "Aux packaging (P2 / P4)",
        "description": "Auxiliary packaging shared by P2 and P4 (rolled up into base_rm stock at ERP load).",
        "bucket": "base_rm",
    },
    6: {
        "short": "Aux packaging (P1 / P4)",
        "description": "Auxiliary packaging shared by P1 and P4 (rolled up into base_rm stock at ERP load).",
        "bucket": "base_rm",
    },
    7: {
        "short": "Drink upper film (BASKISIZ / CPP)",
        "description": "Upper film for drink cups (BASKISIZ UST FILM, FILM CPP) — P3/P4.",
        "bucket": "rm7",
    },
    8: {
        "short": "Drink cartons (KOLI / KUTU)",
        "description": "Shipping cartons for drinks (KOLI, KUTU) — P3/P4.",
        "bucket": "rm8",
    },
    9: {
        "short": "Aux packaging (P1 / P2)",
        "description": "Auxiliary packaging shared by P1 and P2 (rolled up into base_rm stock at ERP load).",
        "bucket": "base_rm",
    },
    10: {
        "short": "Aux packaging (P4 only)",
        "description": "Auxiliary packaging used by P4 only (rolled up into base_rm stock at ERP load).",
        "bucket": "base_rm",
    },
}


# Human-readable ERP bucket labels (initial-state keys).
RM_BUCKET_LABELS: dict[str, dict[str, str]] = {
    "base_rm": {
        "title": "Base RM stock (bulk ingredients + misc. packaging)",
        "description": "Bulk ingredients (AROMA, GLIKOZ, KALSIYUM, SODYUM ALJINAT, MALTODEKSTRIN, fruit concentrates) plus miscellaneous packaging. Covers RM1, RM2, RM3, RM5, RM6, RM9, RM10.",
    },
    "rm4": {
        "title": "RM4 stock — Bubble packaging (KOVA-KAPAK / ETIKET)",
        "description": "Bucket packaging and labels (KOVA-KAPAK, GOVDE ETIKET). Used by P1 (3.4L boba bucket) and P3 (cup boba).",
    },
    "rm7": {
        "title": "RM7 stock — Drink upper film (BASKISIZ / FILM CPP)",
        "description": "Upper film for drink cups (BASKISIZ UST FILM, FILM CPP). Used by P3 and P4.",
    },
    "rm8": {
        "title": "RM8 stock — Drink cartons (KOLI / KUTU)",
        "description": "Shipping cartons (KOLI, KUTU). Used by P3 and P4.",
    },
}


def rm_label(material_id: int) -> str:
    """Return the short human-readable label for an RM id, or 'RM{n}' if unknown."""
    entry = RM_LABELS.get(int(material_id))
    if entry:
        return f"RM{material_id} — {entry['short']}"
    return f"RM{material_id}"


def sayim_is_finished_product_name(urun_ismi: str | None) -> bool:
    """True if ÜRÜN İSMİ is sellable finished / semi-finished stock (not RM packaging line).

    Uses upper-case **product name** substrings (primary signal per ERP RM rollup plan).
    """
    if urun_ismi is None:
        return False
    n = str(urun_ismi).upper().strip()
    if not n:
        return False
    if "POPPING BUBBLE CUP" in n:
        return True
    if "BUBBLETEA KUTU" in n:
        return True
    if "YARIMAMUL" in n:
        return True
    if ("60ML" in n or "60 ML" in n) and ("KOVA" in n or "BOBA" in n):
        if "ETIKET" not in n and "ETİKET" not in n:
            return True
    if ("3.4" in n or "3,4" in n) and ("KOVA" in n or "BUCKET" in n):
        if "ETIKET" not in n and "ETİKET" not in n:
            return True
    if "TENEKE" in n and "3LT" in n and "BUBBLETEA" not in n:
        return True
    return False


def sayim_row_rm_bucket(urun_ismi: str | None, aciklama: str | None) -> RmBucket | None:
    """Map SAYIM row to base_rm / rm4 / rm7 / rm8 using ÜRÜN İSMİ first; AÇIKLAMA fallback.

    Returns None if the row is finished product stock or cannot be classified as RM.
    """
    if sayim_is_finished_product_name(urun_ismi):
        return None
    n = (str(urun_ismi).upper().strip() if urun_ismi else "")

    # Packaging / specific materials (name-first, most specific first)
    if "KOVA-KAPAK" in n:
        return "rm4"
    if "GOVDE ETIKET" in n or ("GÖVDE" in n and ("ETIKET" in n or "ETİKET" in n)):
        return "rm4"
    if "ETIKET" in n or "ETİKET" in n:
        return "rm4"
    if "BASKISIZ" in n or ("FILM" in n and "CPP" in n) or "UST FILM" in n or "ÜST FILM" in n:
        return "rm7"
    if ("KOLI" in n or "KUTU" in n) and "BUBBLETEA" not in n and "POPPING" not in n:
        return "rm8"

    # Bulk ingredients (name keywords)
    ingredient_markers = (
        "AROMA", "GLIKOZ", "MALTODEKSTRIN", "KALSIYUM", "SODYUM", "ALJINAT",
        "KONSANTRE", "KONSANTRESI", "ELMA SUYU", "TOZ ", "NANE ", "MUZ ",
        "CIKOLATA", "LIMON", "MANGO", "NAR ", "AHUDUDU", "ANANAS", "CILEK",
        "YABANMERSINI", "YESIL ELMA", "HINDISTAN CEVIZI", "KARAMEL", "VISNE",
        "LYCHEE", "PASSION", "CARKIFELEK", "RED GRAPE", "STRAWBERRY", "BUBBLE GUM",
    )
    if any(m in n for m in ingredient_markers):
        return "base_rm"

    # Fallback: AÇIKLAMA classification
    if aciklama is None:
        return None
    if isinstance(aciklama, float) and math.isnan(aciklama):
        return None
    cat = classify_aciklama(aciklama)
    if cat == "finished_or_semi":
        return None
    if cat in ("ingredient_bubble_core", "ingredient_flavor_all_products", "ingredient_concentrate_all_products"):
        return "base_rm"
    if cat == "packaging_bubble":
        return "rm4"
    if cat == "packaging_drink":
        a = str(aciklama).upper()
        if "FILM" in a or "BASKISIZ" in a:
            return "rm7"
        if "KOLI" in a or "KUTU" in a:
            return "rm8"
        return "rm7"
    if cat == "other":
        return None
    return None


def classify_aciklama(aciklama: str | None) -> str:
    """Return a coarse class label for an ERP description column."""
    if aciklama is None or (isinstance(aciklama, float) and str(aciklama) == "nan"):
        return "unknown"
    s = str(aciklama).strip().upper()
    if not s:
        return "unknown"
    if s in ERP_CATEGORY_TO_PRODUCTS:
        return "finished_or_semi"
    if s in BUBBLE_CORE_CATEGORIES:
        return "ingredient_bubble_core"
    if s in FLAVOR_ALL_PRODUCTS_CATEGORIES:
        return "ingredient_flavor_all_products"
    for sub in FRUIT_CONCENTRATE_SUBSTRINGS:
        if sub in s:
            return "ingredient_concentrate_all_products"
    if s in BUBBLE_PACKAGING_CATEGORIES:
        return "packaging_bubble"
    for sub in DRINK_PACKAGING_SUBSTRINGS:
        if sub in s:
            return "packaging_drink"
    return "other"
