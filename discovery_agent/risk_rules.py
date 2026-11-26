"""Deterministic red-flag rules, run on every catalog record before the Risk Assessor agent.

Why rules and an agent? Rules are cheap, repeatable and testable, and they catch what can be
read from structured fields. The agent adds judgement flags (conflicts, consent gaps,
representativeness, ...) and may dismiss a rule flag only with a written reason, and the
orchestrator enforces that.

Each rule: (record, candidate, use_case, settings) -> list of {"code", "evidence"}.
"""
from __future__ import annotations

import re
from datetime import date

Flag = dict

GRAIN_ORDER = ["minute", "15min", "30min", "hourly", "daily", "weekly", "monthly", "quarterly", "annual"]
INACTIVE_STATUSES = {"deprecated", "archived", "frozen", "retired", "decommissioned", "superseded"}


def _flag(code: str, evidence: str) -> Flag:
    return {"code": code, "evidence": evidence}


def _d(value: str | None) -> date | None:
    if not isinstance(value, str) or not value:  # a number, list or dict is not a date (a dict would raise KeyError below)
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Provided rules (read these as worked examples)
# ---------------------------------------------------------------------------
def rule_licence(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    if record["kind"] == "internal":
        return []
    lic = record.get("licence") or {}
    name = (lic.get("name") or "").strip()
    flags = []
    if not name or name.lower() in {"unknown", "none", "null", "not found", "n/a"}:
        flags.append(_flag("LIC-UNKNOWN", f"No licence established. Evidence field: {lic.get('evidence')!r}"))
    elif re.search(r"\bNC\b|non[- ]?commercial", name, re.I):
        flags.append(_flag("LIC-NONCOMMERCIAL", f"Licence {name!r} restricts commercial use"))
    elif re.search(r"\bBY\b|attribution|OGL|open government", name, re.I):
        flags.append(_flag("LIC-ATTRIBUTION", f"Licence {name!r} requires attribution"))
    if lic.get("mixed_sources"):
        flags.append(_flag("LIC-MIXED", "Record states that parts come from upstream providers with different terms"))
    return flags


def rule_agreement(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    status = ((record.get("licence") or {}).get("agreement_status") or "").lower()
    if record["kind"] == "vendor_feed" and status not in {"active", "signed"}:
        return [_flag("LIC-AGREEMENT-NOT-ACTIVE", f"Vendor feed with agreement_status={status or 'unknown'!r}")]
    return []


def rule_access(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    acc = record.get("access") or {}
    flags = []
    if acc.get("auth_required") or (acc.get("classification") or "").lower() == "restricted":
        flags.append(_flag("ACC-RESTRICTED", f"auth_required={acc.get('auth_required')}, "
                                             f"classification={acc.get('classification')}, process={acc.get('request_process')!r}"))
    if (acc.get("method") or "").lower() in {"manual_export", "manual", "spreadsheet", "email"}:
        flags.append(_flag("ACC-MANUAL", f"Access method {acc.get('method')!r}"))
    if acc.get("reachable") is False:
        flags.append(_flag("ACC-UNREACHABLE", "Record states the source could not be reached or restored"))
    return flags


def rule_payload(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    size = (record.get("access") or {}).get("approx_size_bytes")
    limit = settings["rules"]["large_payload_bytes"]
    if isinstance(size, int) and size > limit:
        return [_flag("OPS-LARGE-PAYLOAD", f"approx_size_bytes={size:,} > {limit:,}")]
    return []


def rule_pii(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    pii_fields = [f["name"] for f in (record.get("schema") or {}).get("fields", []) if f.get("pii") is True]
    declared = (record.get("declared_metadata") or {}).get("contains_pii")
    if pii_fields or declared is True:
        return [_flag("GOV-PII", f"PII fields: {pii_fields or 'declared contains_pii=true'}")]
    return []


def rule_owner(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    if record["kind"] == "internal" and not ((record.get("ownership") or {}).get("owner") or "").strip():
        return [_flag("GOV-OWNER-UNKNOWN", "Internal source with no recorded owner")]
    return []


def rule_status(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    status = (record.get("status") or "").lower()
    if status in INACTIVE_STATUSES:
        return [_flag("GOV-DEPRECATED", f"status={status!r}")]
    return []


# ---------------------------------------------------------------------------
# G4: three rules. tests/test_learner_gaps.py::test_g4_* checks them.
# ---------------------------------------------------------------------------
def rule_temporal_coverage(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """Coverage of the candidate's target windows, plus staleness.

    - Skip records whose temporal.grain is "static", or whose start is unknown.
    - Treat a null end as "still updating", i.e. covered up to uc["as_of"].
    - For each window id in candidate["target_windows"], compute the fraction of that window
      (uc["windows"], inclusive dates) covered by [start, end].
        all fractions == 0                                      -> COV-OUT-OF-WINDOW
        otherwise any fraction < settings["rules"]["partial_window_threshold"] -> COV-PARTIAL-WINDOW
    - FRS-STALE if end is not null and end is more than settings["rules"]["stale_after_years"]
      years before uc["as_of"].
    Evidence strings must name the window(s) and the dates you compared.
    """
    temporal = record.get("temporal") if isinstance(record.get("temporal"), dict) else {}
    start, end = _d(temporal.get("start")), _d(temporal.get("end"))
    # An end that is given but is not a real date (e.g. "2005-02-29") is unknown, not "still updating": skip, as for a start.
    end_unknown = temporal.get("end") is not None and end is None
    if temporal.get("grain") == "static" or start is None or end_unknown:
        return []
    # The use case is validated (validate-use-case): as_of and the window dates are YYYY-MM-DD, start <= end.
    as_of = date.fromisoformat(uc["as_of"])
    windows = {w["id"]: (date.fromisoformat(w["start"]), date.fromisoformat(w["end"])) for w in uc["windows"]}
    threshold, stale_years = settings["rules"]["partial_window_threshold"], settings["rules"]["stale_after_years"]
    covered_to = end or as_of  # a null end means "still updating": count it as covered up to the as-of date
    source = f"{start}..{end}" if end else f"{start}..(still updating, counted to the as-of date {as_of})"
    targets = candidate.get("target_windows")
    target_ids = [w for w in targets if isinstance(w, str)] if isinstance(targets, list) else []
    coverage = []  # (window id, window start, window end, days covered, days in the window), both ends inclusive
    for wid in dict.fromkeys(target_ids):  # a window id the use case does not define is ignored
        if wid in windows:
            w_start, w_end = windows[wid]
            covered = max(0, (min(covered_to, w_end) - max(start, w_start)).days + 1)
            coverage.append((wid, w_start, w_end, covered, (w_end - w_start).days + 1))
    flags = []
    if coverage and all(covered == 0 for _, _, _, covered, _ in coverage):  # out of window wins over partial
        flags.append(_flag("COV-OUT-OF-WINDOW", f"Source dates {source} do not overlap its target window(s): {_coverage_text(coverage)}"))
    else:
        short = [c for c in coverage if c[3] / c[4] < threshold]
        if short:
            flags.append(_flag("COV-PARTIAL-WINDOW",
                               f"Source dates {source} cover less than {threshold * 100:g}% of: {_coverage_text(short)}"))
    stale_before = _years_before(as_of, stale_years)
    if end and end < stale_before:  # measured from the data's end date, never from a metadata "last updated" date
        flags.append(_flag("FRS-STALE", f"Data end {end} is more than {stale_years} years before the as-of date {as_of} "
                                        f"(cut-off {stale_before}). Source dates {source}; target window(s): "
                                        f"{_coverage_text(coverage) or 'none'}"))
    return flags


def _coverage_text(coverage: list[tuple]) -> str:
    """e.g. "prototype 2004-03-10..2005-04-04: 94 of 391 days (24.0%)". The percentage is rounded down, so a window
    just under the threshold never reads as reaching it."""
    return "; ".join(f"{wid} {w_start}..{w_end}: {covered} of {days} days ({covered * 1000 // days / 10}%)"
                     for wid, w_start, w_end, covered, days in coverage)


def _years_before(day: date, years: int) -> date:
    """The same calendar date `years` years earlier; 29 February becomes 28 February in a non-leap year."""
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)


def rule_grain(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """COV-GRAIN-MISMATCH if the record's grain is coarser than min_grain of any need the
    candidate serves (candidate["need_ids"] -> uc["needs"]). Only grains in GRAIN_ORDER are
    comparable; "event", "static" and "unknown" on either side never raise the flag."""
    temporal = record.get("temporal") if isinstance(record.get("temporal"), dict) else {}
    grain = temporal.get("grain")
    if grain not in GRAIN_ORDER:  # "event", "static", "unknown" or no grain at all: not comparable
        return []
    min_grain = {n["id"]: n["min_grain"] for n in uc["needs"]}  # the use case is validated: every need has a valid min_grain
    need_ids = candidate.get("need_ids") if isinstance(candidate.get("need_ids"), list) else []
    too_coarse = []
    for nid in dict.fromkeys(n for n in need_ids if isinstance(n, str)):  # a need id the use case does not define is ignored
        needed = min_grain.get(nid)
        if needed in GRAIN_ORDER and GRAIN_ORDER.index(grain) > GRAIN_ORDER.index(needed):  # strict: any coarser grain
            too_coarse.append(f"{nid} (needs {needed} or finer)")
    if not too_coarse:
        return []
    return [_flag("COV-GRAIN-MISMATCH", f"Source grain {grain!r} is coarser than the minimum grain of: {', '.join(too_coarse)}")]


# Negated mentions, removed before matching: "no missing values", "without missing data", "free of NaN",
# "does not contain any null values", "none of the readings are missing" ("not only missing values" is not a negation).
_NEGATED = re.compile(r"\b(?:no|not(?!\s+only)|zero|without|never|free\s+of|none\s+of\s+the)(?:\s+\w+){0,2}?\s+"
                      r"(?:missing|null|nan|empty|absent)\w*", re.I)
# The label form some pages use: "Has Missing Values? No", "Missing attribute values: none".
_NEGATED_LABEL = re.compile(r"\bmissing\s+(?:\w+\s+)?values?\s*[?:]?\s*(?:no|none|false|0|n/a)\b", re.I)
# What describes missing values. A bare "missing" or "?" is not enough ("Licence is missing", "Has Missing Values? No").
_MISSING_CUE = re.compile(
    r"\bmissing\s+(?:\w+\s+)?(?:values?|data|readings?|measurements?|observations?|entries|records?|cells?|rows?|hours?|days?)\b"
    r"|\b(?:values?|data|readings?|measurements?|observations?|entries|records?)\s+(?:are|is|were|was)\s+(?:missing|absent)\b"
    r"|\babsence\s+of\s+(?:a\s+)?values?\b|\bnull\s+(?:values?|entries|cells)\b|(?-i:\b(?:NaN|nan|NAN)\b)"
    r"|(?<![\w.])[-\u2212](?:200|999|9999)(?:\.0+)?(?!\d|\.\d)"  # sentinel codes: -200, -999.0; not -2000 or -200.5
    r"|['\"‘’“”]\?['\"‘’“”]",  # a quoted '?' used as the missing marker
    re.I)


def rule_metadata_contradiction(record: dict, candidate: dict, uc: dict, settings: dict) -> list[Flag]:
    """DQ-METADATA-CONTRADICTION when record["declared_metadata"]["has_missing_values"] is a
    'no' (False, "no", "false") but documentation_excerpts or quality_notes describe missing
    values (e.g. "missing values", "absence of value", "-200", "?" used as missing, "NaN").
    Careful: "Data set has no missing values" is NOT a contradiction. Strip negated phrases
    before matching."""
    declared = record.get("declared_metadata") if isinstance(record.get("declared_metadata"), dict) else {}
    value = declared.get("has_missing_values")
    if not (value is False or (isinstance(value, str) and value.strip().lower() in {"no", "false"})):
        return []  # only a declared "no" can be contradicted: None, an absent key or "yes" never fire
    for field in ("documentation_excerpts", "quality_notes"):  # not sample_findings: a sample's gaps are DQ-SENTINEL-VALUES
        texts = record.get(field) if isinstance(record.get(field), list) else []
        for i, text in enumerate(texts):
            if not isinstance(text, str):
                continue
            cue = _MISSING_CUE.search(_NEGATED.sub(" ", _NEGATED_LABEL.sub(" ", text)))  # strip negations first, then match
            if cue:
                return [_flag("DQ-METADATA-CONTRADICTION",
                              f"declared_metadata.has_missing_values is {value!r}, but {field}[{i}] describes missing values "
                              f"({cue.group(0)!r}): {text[:300]!r}")]
    return []


RULES = [rule_licence, rule_agreement, rule_access, rule_payload, rule_pii, rule_owner, rule_status,
         rule_temporal_coverage, rule_grain, rule_metadata_contradiction]


def evaluate(record: dict, candidate: dict, uc: dict, settings: dict) -> tuple[list[Flag], list[str]]:
    """Run every rule. Returns (flags, warnings). A rule that is not implemented yet is skipped with a warning."""
    flags: list[Flag] = []
    warnings: list[str] = []
    for rule in RULES:
        try:
            for f in rule(record, candidate, uc, settings):
                flags.append({**f, "raised_by": f"rule:{rule.__name__}"})
        except NotImplementedError as exc:
            warnings.append(f"{rule.__name__} skipped: {exc}")
    seen, unique = set(), []
    for f in flags:
        if f["code"] not in seen:
            seen.add(f["code"])
            unique.append(f)
    return unique, warnings
