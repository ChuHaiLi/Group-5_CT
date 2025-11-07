"""
Smart Travel Project — Single-File Implementation


This single Python module bundles:
- Taxonomy (languages, currencies, countries, interests)
- JSON Schemas (user profile, user query)
- Normalization utilities (language, currency, country, interests, budget parsing)
- Validation pipeline (JSON Schema + custom logical checks)
- UX error mapping (friendly codes/messages)
- Minimal test fixtures and a CLI with `--test` and `--preview`

Usage:
    python smart_travel_single.py --test     # Run embedded fixtures through normalize+validate
    python smart_travel_single.py --preview  # Demo normalize+validate with defaults from a profile

Notes:
- Requires Python 3.10+
- If `jsonschema` is installed, strict schema validation runs. If not, the script still
  demonstrates normalization and prints a notice.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Optional dependency: jsonschema
try:
    import jsonschema
    from jsonschema import Draft7Validator
except Exception:
    jsonschema = None
    Draft7Validator = None  # type: ignore

# --------------------------------------------------------------------------------------
# Embedded Taxonomy (acts as the source of truth for normalization)
# --------------------------------------------------------------------------------------
TAXONOMY: Dict[str, Any] = {
    "version": "1.0",
    "languages": [
        {"preferred": "en-US", "aliases": ["en", "en-US", "English", "english"]},
        {"preferred": "fr-FR", "aliases": ["fr", "fr-FR", "French", "french"]},
        {"preferred": "es-ES", "aliases": ["es", "es-ES", "Spanish", "spanish"]},
        {"preferred": "zh-CN", "aliases": ["zh", "zh-CN", "Chinese", "chinese", "zh-cn"]},
        {"preferred": "ja-JP", "aliases": ["ja", "ja-JP", "Japanese", "japanese"]},
    ],
    "currencies": [
        {"preferred": "USD", "aliases": ["USD", "usd", "$", "US Dollar", "dollar", "dollars"]},
        {"preferred": "EUR", "aliases": ["EUR", "eur", "€", "Euro", "euro"]},
        {"preferred": "GBP", "aliases": ["GBP", "gbp", "£", "Pound", "British Pound"]},
        {"preferred": "JPY", "aliases": ["JPY", "jpy", "¥", "Yen", "yen", "Japanese Yen"]},
    ],
    "countries": [
        {"preferred": "US", "aliases": ["US", "USA", "United States", "United States of America"]},
        {"preferred": "GB", "aliases": ["GB", "UK", "United Kingdom", "Great Britain"]},
        {"preferred": "FR", "aliases": ["FR", "France", "French Republic"]},
        {"preferred": "VN", "aliases": ["VN", "Vietnam", "Viet Nam"]},
        {"preferred": "JP", "aliases": ["JP", "Japan"]},
        {"preferred": "CN", "aliases": ["CN", "China", "PRC", "People's Republic of China"]},
        {"preferred": "DE", "aliases": ["DE", "Germany"]},
    ],
    "interests": [
        {"preferred": "beach", "aliases": ["beach", "beaches", "coastal", "Beach"]},
        {"preferred": "culture", "aliases": ["culture", "cultural", "history", "Culture"]},
        {"preferred": "adventure", "aliases": ["adventure", "Adventure", "adrenaline", "extreme"]},
        {"preferred": "nature", "aliases": ["nature", "Nature", "wildlife", "outdoors"]},
        {"preferred": "food", "aliases": ["food", "Food", "cuisine", "gastronomy"]},
    ],
}

# --------------------------------------------------------------------------------------
# Embedded JSON Schemas (draft-07)
# --------------------------------------------------------------------------------------
USER_PROFILE_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "UserProfile",
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "name": {"type": "string"},
        "language_preference": {"type": "string", "enum": ["en-US", "fr-FR", "es-ES", "zh-CN", "ja-JP"]},
        "currency_preference": {"type": "string", "enum": ["USD", "EUR", "GBP", "JPY"]},
        "home_country": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "interests": {
            "type": "array",
            "items": {"type": "string", "enum": ["beach", "culture", "adventure", "nature", "food"]},
        },
    },
    "required": ["user_id", "language_preference", "currency_preference"],
}

USER_QUERY_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "UserQuery",
    "type": "object",
    "properties": {
        "origin": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "destination": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "departure_date": {"type": "string", "format": "date"},
        "return_date": {"type": "string", "format": "date"},
        "adults": {"type": "integer", "minimum": 1},
        "children": {"type": "integer", "minimum": 0},
        "language": {"type": "string", "enum": ["en-US", "fr-FR", "es-ES", "zh-CN", "ja-JP"]},
        "currency": {"type": "string", "enum": ["USD", "EUR", "GBP", "JPY"]},
        "interests": {
            "type": "array",
            "items": {"type": "string", "enum": ["beach", "culture", "adventure", "nature", "food"]},
        },
        "budget": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "minimum": 0},
                "currency": {"type": "string", "enum": ["USD", "EUR", "GBP", "JPY"]},
            },
            "required": ["amount"],
        },
    },
    "required": ["origin", "destination", "departure_date", "return_date", "adults"],
}

# --------------------------------------------------------------------------------------
# UX Error Catalog (code -> message + hint). Used for mapping validation failures.
# --------------------------------------------------------------------------------------
UX_ERRORS: Dict[str, Dict[str, str]] = {
    "REQ_FIELD_MISSING": {
        "message": "The field '{field}' is required.",
        "hint": "Please provide a value for the '{field}' field.",
    },
    "INVALID_TYPE": {"message": "Invalid data type for '{field}'.", "hint": "Please enter a valid value."},
    "INVALID_DATE_FORMAT": {
        "message": "Date must be in YYYY-MM-DD format.",
        "hint": "Use the date format YYYY-MM-DD (e.g., 2025-12-01).",
    },
    "DATE_ORDER": {
        "message": "Return date is earlier than departure date.",
        "hint": "Ensure the return date is on or after the departure date.",
    },
    "ADULT_COUNT_MIN": {"message": "At least one adult is required.", "hint": "Set adults to 1 or more."},
    "CHILD_COUNT_MIN": {
        "message": "Children count cannot be negative.",
        "hint": "Use 0 or a positive number for children.",
    },
    "UNSUPPORTED_LANGUAGE": {
        "message": "Unsupported language selection.",
        "hint": "Choose a supported language (e.g., 'en-US').",
    },
    "UNSUPPORTED_CURRENCY": {
        "message": "Unsupported currency code.",
        "hint": "Use a valid ISO 4217 code (e.g., USD, EUR).",
    },
    "UNSUPPORTED_INTEREST": {
        "message": "Unsupported interest category.",
        "hint": "Choose from the available categories (beach, culture, adventure, nature, food).",
    },
    "INVALID_COUNTRY_CODE": {
        "message": "Invalid country code for '{field}'.",
        "hint": "Use a 2-letter ISO 3166-1 code (e.g., 'US').",
    },
    "INVALID_VALUE": {"message": "Invalid value for '{field}'.", "hint": "Please correct the input."},
}

# --------------------------------------------------------------------------------------
# Normalization Utilities
# --------------------------------------------------------------------------------------
def _build_alias_map(category_list: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a case-insensitive alias -> preferred mapping for a taxonomy category."""
    mapping: Dict[str, str] = {}
    for entry in category_list:
        preferred = entry["preferred"]
        for alias in entry.get("aliases", []):
            mapping[alias.lower()] = preferred
    return mapping

_LANGUAGE_MAP = _build_alias_map(TAXONOMY["languages"])
_CURRENCY_MAP = _build_alias_map(TAXONOMY["currencies"])
_COUNTRY_MAP = _build_alias_map(TAXONOMY["countries"])
_INTEREST_MAP = _build_alias_map(TAXONOMY["interests"])


def normalize_language(lang: Optional[str]) -> Optional[str]:
    """Return canonical BCP-47 tag (e.g., 'English' -> 'en-US'). Preserve unknowns."""
    if not lang:
        return lang
    raw = lang.strip()
    if raw.lower() in _LANGUAGE_MAP:
        return _LANGUAGE_MAP[raw.lower()]
    m = re.match(r"^([A-Za-z]{2,3})(?:-([A-Za-z]{2}))?$", raw)
    if m:
        lc = m.group(1).lower()
        rc = m.group(2)
        return f"{lc}-{rc.upper()}" if rc else lc
    return raw


def normalize_currency(curr: Optional[str]) -> Optional[str]:
    """Return canonical ISO-4217 code (e.g., '€' -> 'EUR'). Preserve unknown symbols as-is."""
    if not curr:
        return curr
    raw = curr.strip()
    if raw.lower() in _CURRENCY_MAP:
        return _CURRENCY_MAP[raw.lower()]
    if raw.isalpha() and len(raw) == 3:
        return raw.upper()
    return raw


def normalize_country(country: Optional[str]) -> Optional[str]:
    """Return ISO 3166-1 alpha-2 code (e.g., 'United States' -> 'US')."""
    if not country:
        return country
    raw = country.strip()
    if raw.lower() in _COUNTRY_MAP:
        return _COUNTRY_MAP[raw.lower()]
    if len(raw) == 2 and raw.isalpha():
        return raw.upper()
    if len(raw) == 3 and raw.isalpha():
        return raw.upper()
    return raw


def normalize_interests(interests: Any) -> Optional[List[str]]:
    """Normalize a list or comma-separated string of interest keywords to canonical set."""
    if interests is None:
        return None
    parts: List[str]
    if isinstance(interests, str):
        parts = [p.strip() for p in interests.split(",") if p.strip()]
    elif isinstance(interests, list):
        parts = interests
    else:
        parts = []
    out: List[str] = []
    for item in parts:
        if not isinstance(item, str):
            continue
        key = item.strip().lower()
        out.append(_INTEREST_MAP.get(key, key))
    # de-duplicate while preserving order
    seen: set[str] = set()
    uniq: List[str] = []
    for v in out:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def normalize_user_profile(profile: Dict[str, Any] | None) -> Dict[str, Any] | None:
    """Normalize a raw profile dict. Unknown values are preserved for validator to catch."""
    if profile is None:
        return None
    norm: Dict[str, Any] = {}
    for k, v in profile.items():
        if v is None:
            norm[k] = None
            continue
        if k == "language_preference":
            norm[k] = normalize_language(str(v))
        elif k == "currency_preference":
            norm[k] = normalize_currency(str(v))
        elif k == "home_country":
            norm[k] = normalize_country(str(v))
        elif k == "interests":
            norm[k] = normalize_interests(v)
        else:
            # best-effort numeric coercion for unknown fields
            if isinstance(v, str):
                if v.isdigit():
                    try:
                        norm[k] = int(v)
                        continue
                    except ValueError:
                        pass
                try:
                    f = float(v)
                    norm[k] = int(f) if f.is_integer() else f
                    continue
                except ValueError:
                    pass
            norm[k] = v
    return norm


def _parse_budget_str(s: str) -> Optional[Dict[str, Any]]:
    """Parse budget strings like '5000 USD', '$3000', '€1200'. Returns dict or None."""
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z$€£¥]*)\s*$", s)
    if not m:
        return None
    amount_s, curr_s = m.groups()
    try:
        amount = int(amount_s) if amount_s.isdigit() else float(amount_s)
    except ValueError:
        return None
    result: Dict[str, Any] = {"amount": amount}
    if curr_s:
        result["currency"] = normalize_currency(curr_s)
    return result


def normalize_user_query(query: Dict[str, Any] | None, profile: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
    """Normalize a raw query, applying defaults from `profile` when helpful (origin, currency)."""
    if query is None:
        return None
    out: Dict[str, Any] = {}
    origin_default = (profile or {}).get("home_country") if profile else None
    for k, v in query.items():
        if v is None:
            continue
        if k == "language":
            out[k] = normalize_language(str(v))
        elif k == "currency":
            out[k] = normalize_currency(str(v))
        elif k in ("origin", "destination"):
            out[k] = normalize_country(str(v))
        elif k == "interests":
            out[k] = normalize_interests(v)
        elif k == "budget":
            if isinstance(v, str):
                parsed = _parse_budget_str(v)
                out[k] = parsed if parsed is not None else v
            elif isinstance(v, (int, float)):
                out[k] = {"amount": v}
            elif isinstance(v, dict):
                amt = v.get("amount")
                cur = v.get("currency")
                if isinstance(amt, str):
                    try:
                        f = float(amt)
                        amt = int(f) if f.is_integer() else f
                    except ValueError:
                        pass
                out[k] = {"amount": amt}
                if cur:
                    out[k]["currency"] = normalize_currency(str(cur))
            else:
                out[k] = v
        else:
            # best-effort numeric coercion for adults/children if given as strings
            if isinstance(v, str):
                if v.isdigit():
                    try:
                        out[k] = int(v)
                        continue
                    except ValueError:
                        pass
                try:
                    f = float(v)
                    out[k] = int(f) if f.is_integer() else f
                    continue
                except ValueError:
                    pass
            out[k] = v
    # Defaults from profile
    if not out.get("origin") and origin_default:
        out["origin"] = normalize_country(str(origin_default))
    if isinstance(out.get("budget"), dict):
        b = out["budget"]
        if b.get("amount") is not None and not b.get("currency") and profile and profile.get("currency_preference"):
            b["currency"] = profile["currency_preference"]
    return out

# --------------------------------------------------------------------------------------
# Validation helpers
# --------------------------------------------------------------------------------------
@dataclass
class ValidationIssue:
    code: str
    field: str | None = None
    message: str | None = None
    hint: str | None = None


def _map_schema_error(err: Any, profile: bool = False) -> ValidationIssue:
    """Translate jsonschema.ValidationError to our UX error taxonomy."""
    # Safe defaults
    field = ".".join(str(p) for p in err.path) if getattr(err, "path", None) else None
    code = "INVALID_VALUE"
    if getattr(err, "validator", None) == "required":
        code = "REQ_FIELD_MISSING"
        # Try to extract field name from message
        m = re.search(r"'([^']+)' is a required property", err.message)
        if m:
            field = m.group(1)
    elif getattr(err, "validator", None) == "enum":
        # Deduce domain-specific codes
        target = field or ""
        if any(x in target for x in ["language_preference", "language"]):
            code = "UNSUPPORTED_LANGUAGE"
        elif "currency" in target:
            code = "UNSUPPORTED_CURRENCY"
        elif target.startswith("interests"):
            code = "UNSUPPORTED_INTEREST"
        else:
            code = "INVALID_VALUE"
    elif getattr(err, "validator", None) == "pattern":
        code = "INVALID_COUNTRY_CODE" if field and ("origin" in field or "destination" in field or "country" in field) else "INVALID_VALUE"
    elif getattr(err, "validator", None) == "format":
        code = "INVALID_DATE_FORMAT"
    elif getattr(err, "validator", None) == "minimum":
        if field == "adults":
            code = "ADULT_COUNT_MIN"
        elif field == "children":
            code = "CHILD_COUNT_MIN"
        else:
            code = "INVALID_VALUE"
    elif getattr(err, "validator", None) == "type":
        code = "INVALID_TYPE"
    # Compose message/hint
    u = UX_ERRORS.get(code, {"message": "Invalid value.", "hint": "Please correct it."})
    msg = u["message"].replace("{field}", field or "field")
    hint = u.get("hint", "")
    return ValidationIssue(code=code, field=field, message=msg, hint=hint)


def validate_profile(profile: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if jsonschema:
        validator = Draft7Validator(USER_PROFILE_SCHEMA)  # type: ignore
        for err in validator.iter_errors(profile):
            issues.append(_map_schema_error(err, profile=True))
    return issues


def validate_query(query: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if jsonschema:
        validator = Draft7Validator(USER_QUERY_SCHEMA)  # type: ignore
        for err in validator.iter_errors(query):
            issues.append(_map_schema_error(err, profile=False))
        # Custom logical check: return_date >= departure_date
        try:
            dep = datetime.fromisoformat(query["departure_date"])  # may KeyError
            ret = datetime.fromisoformat(query["return_date"])    # may KeyError
            if ret < dep:
                u = UX_ERRORS["DATE_ORDER"]
                issues.append(ValidationIssue(code="DATE_ORDER", message=u["message"], hint=u["hint"]))
        except Exception:
            # If dates missing or malformed, schema will already have produced issues
            pass
    return issues

# --------------------------------------------------------------------------------------
# Minimal embedded fixtures for demo/testing (mirrors the multi-file repo’s samples)
# --------------------------------------------------------------------------------------
PROFILE_FIXTURES: List[Dict[str, Any]] = [
    {
        "id": "P1",
        "profile": {
            "user_id": "U001",
            "name": "Alice",
            "language_preference": "English",
            "currency_preference": "$",
            "home_country": "United States",
            "interests": ["Beaches", "Culture", "Food"],
        },
        "valid": True,
    },
    {
        "id": "P2",
        "profile": {
            "user_id": "U002",
            "name": "Bob",
            "language_preference": "French",
            "home_country": "France",
            "interests": ["Adventure"],
        },
        "valid": False,
    },
    {
        "id": "P3",
        "profile": {
            "user_id": "U003",
            "name": "Charlie",
            "language_preference": "German",
            "currency_preference": "EUR",
            "home_country": "Germany",
            "interests": ["culture"],
        },
        "valid": False,
    },
    {
        "id": "P4",
        "profile": {
            "user_id": "U004",
            "name": "Diana",
            "language_preference": "es",
            "currency_preference": "AUD",
            "home_country": "AU",
            "interests": ["Nature", "Wildlife"],
        },
        "valid": False,
    },
    {
        "id": "P5",
        "profile": {
            "user_id": "U005",
            "name": "Eve",
            "language_preference": "en",
            "currency_preference": "USD",
            "home_country": "US",
            "interests": ["Shopping", "beach"],
        },
        "valid": False,
    },
]

QUERY_FIXTURES: List[Dict[str, Any]] = [
    {
        "id": "Q1",
        "query": {
            "origin": "US",
            "destination": "FR",
            "departure_date": "2025-12-01",
            "return_date": "2025-12-10",
            "adults": 2,
            "children": 1,
            "interests": ["food", "Culture"],
            "budget": "5000 USD",
        },
        "valid": True,
    },
    {
        "id": "Q2",
        "query": {
            "origin": "US",
            "departure_date": "2025-08-01",
            "return_date": "2025-08-10",
            "adults": 1,
        },
        "valid": False,
    },
    {
        "id": "Q3",
        "query": {
            "origin": "US",
            "destination": "GB",
            "departure_date": "01/06/2025",
            "return_date": "2025-06-10",
            "adults": 2,
        },
        "valid": False,
    },
    {
        "id": "Q4",
        "query": {
            "origin": "US",
            "destination": "US",
            "departure_date": "2025-12-10",
            "return_date": "2025-12-01",
            "adults": 1,
        },
        "valid": False,
    },
    {
        "id": "Q5",
        "query": {
            "origin": "US",
            "destination": "MX",
            "departure_date": "2025-07-01",
            "return_date": "2025-07-10",
            "adults": 0,
            "children": -1,
        },
        "valid": False,
    },
    {
        "id": "Q6",
        "query": {
            "origin": "US",
            "destination": "US",
            "departure_date": "2025-09-01",
            "return_date": "2025-09-10",
            "adults": 2,
            "interests": ["shopping", "beach"],
        },
        "valid": False,
    },
    {
        "id": "Q7",
        "query": {
            "origin": "US",
            "destination": "CA",
            "departure_date": "2025-11-01",
            "return_date": "2025-11-05",
            "adults": 1,
            "budget": "approx 500",
        },
        "valid": False,
    },
    {
        "id": "Q8",
        "query": {
            "origin": "US",
            "destination": "AU",
            "departure_date": "2025-03-01",
            "return_date": "2025-03-10",
            "adults": 1,
            "budget": "1000 AUD",
        },
        "valid": False,
    },
    {
        "id": "Q9",
        "query": {
            "origin": "GB",
            "destination": "JP",
            "departure_date": "2025-04-15",
            "return_date": "2025-04-20",
            "adults": 2,
            "budget": {"amount": "2000", "currency": "cad"},
        },
        "valid": False,
    },
    {
        "id": "Q10",
        "query": {
            "destination": "JP",
            "departure_date": "2025-12-01",
            "return_date": "2025-12-05",
            "adults": 1,
        },
        "valid": False,
    },
]

# --------------------------------------------------------------------------------------
# CLI runners (test & preview)
# --------------------------------------------------------------------------------------

def run_tests() -> int:
    """Execute embedded fixtures through normalize + validate; print a summary.
    Returns process exit code (0 = all pass)."""
    total = 0
    passed = 0
    failures: List[str] = []

    # Profiles
    for t in PROFILE_FIXTURES:
        total += 1
        norm = normalize_user_profile(t["profile"]) or {}
        issues = validate_profile(norm)
        valid = len(issues) == 0
        if valid == bool(t["valid"]):
            passed += 1
        else:
            failures.append(f"{t['id']} FAIL – expected valid={t['valid']} got {valid} – issues={[i.code for i in issues]}")

    # Queries (no profile defaults in bulk test)
    for t in QUERY_FIXTURES:
        total += 1
        norm = normalize_user_query(t["query"], profile=None) or {}
        issues = validate_query(norm)
        valid = len(issues) == 0
        if valid == bool(t["valid"]):
            passed += 1
        else:
            failures.append(f"{t['id']} FAIL – expected valid={t['valid']} got {valid} – issues={[i.code for i in issues]}")

    print(f"Test Results: {passed}/{total} tests passed.")
    if failures:
        print("Detailed Failures:")
        for line in failures:
            print(" - " + line)
    else:
        print("All test cases passed.")

    if jsonschema is None:
        print("(Note) Install 'jsonschema' for strict validation: pip install jsonschema")

    return 0 if passed == total else 1


def run_preview() -> int:
    """Demonstrate normalization+validation with profile defaults (origin, budget currency)."""
    # Choose P1 profile and Q10 query (missing origin) for preview
    profile = next(p["profile"] for p in PROFILE_FIXTURES if p["id"] == "P1")
    query = next(q["query"] for q in QUERY_FIXTURES if q["id"] == "Q10")

    print("Preview Simulation:\n")
    print("Raw User Profile Input:")
    print(json.dumps(profile, indent=2))
    print("\nRaw User Query Input (missing origin):")
    print(json.dumps(query, indent=2))

    norm_profile = normalize_user_profile(profile) or {}
    norm_query = normalize_user_query(query, norm_profile) or {}

    print("\nNormalized User Profile:")
    print(json.dumps(norm_profile, indent=2))
    print("\nNormalized User Query (with profile defaults applied):")
    print(json.dumps(norm_query, indent=2))

    if jsonschema:
        issues = validate_query(norm_query)
        if issues:
            print("\nValidation Issues:")
            for i in issues:
                print(f"- {i.code}: {i.message} Hint: {i.hint}")
        else:
            print("\nThe normalized query passed all validation checks.")
    else:
        print("\n(Note) 'jsonschema' not installed – skipping strict validation.")

    return 0


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Travel – single-file CLI")
    parser.add_argument("--test", action="store_true", help="Run embedded fixture tests")
    parser.add_argument("--preview", action="store_true", help="Preview normalization+validation on an example")
    args = parser.parse_args()

    if args.test:
        sys.exit(run_tests())
    if args.preview:
        sys.exit(run_preview())

    parser.print_help()


if __name__ == "__main__":
    main()
