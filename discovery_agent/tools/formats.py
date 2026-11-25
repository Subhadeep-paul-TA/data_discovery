"""Summarisers for self-describing metadata formats the supplementary URLs use.

The tool wrappers (fetch + call) are provided. jsonstat_summary is the learner's gap G3; the data-package
summary is not graded in this version and stays a stub. Both are pure, so they can be tested offline
against tests/fixtures/ without network or LLM.
"""
from __future__ import annotations

import math
from collections import Counter

from .base import NotImplementedTool, ToolContext, tool

LARGE_RESOURCE_BYTES = 100_000_000


# ---------------------------------------------------------------------------
# Not graded in this version (former G2). Left as a stub: no graded link uses a data package.
# ---------------------------------------------------------------------------
# Spec: https://specs.frictionlessdata.io/data-package/
# Return a dict with EXACTLY these keys (tests/test_learner_gaps.py checks them):
#   title, version, profile          : str | None, copied from the package
#   declared_licences                : the package's "licenses" list, or None if absent/empty
#   temporal                         : {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} from package["temporal"], or None
#   resources                        : [{"name", "path", "format", "bytes", "field_count"}] one per resource
#   total_bytes                      : sum of resource bytes (missing bytes count as 0)
#   largest_resource_bytes           : max resource bytes
#   matching_fields                  : fields whose name starts with any prefix in field_filter (all resources,
#                                      de-duplicated by name, max 60): [{"resource", "name", "unit", "source"}]
#                                      where "source" is field["source"]["name"] if present. [] if field_filter is None.
#   upstream_sources                 : sorted distinct field["source"]["name"] values across ALL fields
#   warnings                         : list containing (when they apply)
#                                        "NO_PACKAGE_LICENCE"         no package-level licence declared
#                                        "LARGE_RESOURCE"             any resource > LARGE_RESOURCE_BYTES
#                                        "MULTIPLE_UPSTREAM_SOURCES"  more than one upstream source
def datapackage_summary(package: dict, field_filter: list[str] | None = None) -> dict:
    raise NotImplementedTool("datapackage_summary is not implemented in this version (former G2).")


# ---------------------------------------------------------------------------
# G3: JSON-stat 2.0 dataset -> summary
# ---------------------------------------------------------------------------
# Spec: https://json-stat.org/full/   (Eurostat's dissemination API returns this format)
# Return a dict with EXACTLY these keys:
#   label, updated, source           : copied from the dataset
#   dimensions                       : [{"id", "size", "labels"}] in the order of dataset["id"];
#                                      labels = first 10 "code: label" strings for that dimension
#   time                             : {"first", "last", "values"} for the "time" dimension (codes, sorted), or None
#   geo_codes                        : list of codes in the "geo" dimension, in index order ([] if no geo dimension)
#   expected_cells                   : product of dataset["size"]
#   value_count                      : number of non-null values (dataset["value"] can be a dict OR a list)
#   missing_cells                    : expected_cells - value_count
#   status_counts                    : {status_code: count} from dataset.get("status") (dict or list), {} if absent
#   warnings                         : list containing (when they apply)
#                                        "MISSING_CELLS"       missing_cells > 0
#                                        "NON_ISO_GEO_CODES"   any geo code that is not ISO 3166-1 alpha-2,
#                                                              including Eurostat's "UK" (ISO: GB) and "EL" (ISO: GR)
#                                                              and aggregates such as "EU27_2020"
# Hint: dimension categories look like
#   dataset["dimension"]["geo"]["category"] = {"index": {"UK": 0, "FR": 1}, "label": {"UK": "United Kingdom", ...}}
#   "index" can also be a list of codes.
def jsonstat_summary(dataset: dict) -> dict:
    """Summarise a JSON-stat 2.0 dataset: its shape, time and geo coverage, how many cells hold a value, status flags.

    The cube has one cell per combination of categories, numbered in row-major order over dataset["id"] (the last
    dimension varies fastest). "value" and "status" give data per cell number: a list is dense (null = no value),
    a dict is sparse ({"cell number": item}). Codes are read in index POSITION order and never translated, so
    Eurostat's "UK" stays "UK" (and raises NON_ISO_GEO_CODES). It never raises: links.py only catches
    NotImplementedTool, so a malformed document gives an empty or partial summary instead of an exception.
    """
    ds = dataset if isinstance(dataset, dict) else {}
    ids = [str(i) for i in ds["id"]] if isinstance(ds.get("id"), list) else []
    dimension = ds.get("dimension") if isinstance(ds.get("dimension"), dict) else {}
    categories = {i: _category(dimension.get(i)) for i in ids}
    codes = {i: _codes(categories[i]) for i in ids}
    sizes = ds.get("size")
    if not (isinstance(sizes, list) and len(sizes) == len(ids) and all(_is_count(s) for s in sizes)):
        sizes = [len(codes[i]) for i in ids]  # a broken "size": count each dimension's categories instead
    expected = math.prod(sizes) if ids else 0
    value_count = sum(1 for _, v in _cells(ds.get("value"), expected) if v is not None)  # 0 is a value; only null is missing
    missing = expected - value_count
    time_id = _find_dimension(ds, ids, "time", ("time", "time_period"))
    geo_id = _find_dimension(ds, ids, "geo", ("geo",))
    time_codes = sorted(codes[time_id]) if time_id else []  # as strings: works for 2005, 2020-01, 2020-Q1, 2020M01
    geo_codes = codes[geo_id] if geo_id else []
    warnings = ["MISSING_CELLS"] if missing > 0 else []
    if any(code not in ISO_3166_ALPHA2 for code in geo_codes):
        warnings.append("NON_ISO_GEO_CODES")
    # Short fields first: the agent cuts a tool result at 14,000 characters, so the long lists come last.
    return {
        "label": ds.get("label"), "updated": ds.get("updated"), "source": ds.get("source"),
        "expected_cells": expected, "value_count": value_count, "missing_cells": missing,
        "status_counts": _status_counts(ds.get("status"), expected), "warnings": warnings,
        "time": {"first": time_codes[0], "last": time_codes[-1], "values": time_codes} if time_codes else None,
        "dimensions": [{"id": i, "size": size, "labels": _labels(categories[i], codes[i])} for i, size in zip(ids, sizes)],
        "geo_codes": geo_codes,
    }


# ISO 3166-1 alpha-2: the 249 officially assigned country codes, as listed in the tz database's iso3166.tab
# (current as of ISO/TC 46 N1127, 2024-02-29); the standard library has no country list. Not in it: Eurostat's
# EL (Greece; ISO GR) and UK (ISO GB), aggregates such as EU27_2020 and EA20, NUTS regions such as ITC4.
ISO_3166_ALPHA2 = frozenset("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ
CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR
GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP
KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS
MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS
RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW
TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())


def _is_count(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def _category(dimension) -> dict:
    category = dimension.get("category") if isinstance(dimension, dict) else None
    return category if isinstance(category, dict) else {}


def _codes(category: dict) -> list[str]:
    """A dimension's codes in index POSITION order. "index" is a list of codes or a dict {code: position}; a dimension
    with a single category may omit it, and then its code comes from "label"."""
    index = category.get("index")
    if isinstance(index, list):
        return [str(code) for code in index]
    if isinstance(index, dict):  # sort by position, not by the dict's own order (a bad position goes last)
        return [str(code) for code in sorted(index, key=lambda code: index[code] if _is_count(index[code]) else len(index))]
    labels = category.get("label")
    return [str(code) for code in labels] if isinstance(labels, dict) else []


def _labels(category: dict, codes: list[str]) -> list[str]:
    """The first 10 categories as "code: label"; a category without a label shows its code."""
    names = category.get("label") if isinstance(category.get("label"), dict) else {}
    return [f"{code}: {names.get(code) or code}" for code in codes[:10]]


def _find_dimension(dataset: dict, ids: list[str], role: str, names: tuple[str, ...]) -> str | None:
    """The dimension with this role: as declared in dataset["role"] (JSON-stat 2.0) first, else by its id."""
    roles = dataset.get("role")
    declared = roles.get(role) if isinstance(roles, dict) else None
    for dim_id in declared if isinstance(declared, list) else []:
        if dim_id in ids:
            return dim_id
    return next((i for i in ids if i.lower() in names), None)


def _cells(data, expected: int):
    """(cell number, item) pairs. A list is dense (item n is cell n); a dict is sparse {"cell number": item}.
    Items for cell numbers outside the cube are ignored, so missing_cells cannot go negative."""
    if isinstance(data, list):
        return enumerate(data[:expected])
    if isinstance(data, dict):
        return {int(k): v for k, v in data.items() if str(k).isdecimal() and int(k) < expected}.items()
    return []


def _status_counts(status, expected: int) -> dict:
    """{flag: number of cells}. A single string flag applies to every cell (JSON-stat 2.0), and so does the deprecated
    one-item list. A flag on a cell without a value still counts (e.g. "c", confidential)."""
    if isinstance(status, list) and len(status) == 1 and expected > 1:
        status = status[0]
    if isinstance(status, str):
        return {status: expected} if status and expected else {}
    return dict(Counter(flag for _, flag in _cells(status, expected) if isinstance(flag, str) and flag))


# ---------------------------------------------------------------------------
# Tool wrappers (provided)
# ---------------------------------------------------------------------------
@tool("summarize_datapackage",
      "Summarise a Frictionless Data Package descriptor (datapackage.json): licence declarations, temporal coverage, "
      "resource sizes, matching fields and their upstream sources. Reads only the descriptor, never the data files.",
      {"url": {"type": "string"},
       "field_filter": {"type": "array", "items": {"type": "string"},
                        "description": "Field-name prefixes to list, e.g. ['AB_', 'CD_load']"}},
      ["url"])
def summarize_datapackage(ctx: ToolContext, args: dict) -> dict:
    package, res = ctx.http.get_json(args["url"], max_bytes=5_000_000, agent=ctx.agent)
    return {"url": args["url"], "last_modified_header": res.headers.get("last-modified"),
            **datapackage_summary(package, args.get("field_filter"))}


@tool("summarize_jsonstat",
      "Summarise a JSON-stat 2.0 dataset (for example from the Eurostat dissemination API): dimensions, time coverage, "
      "geo codes, missing cells and status flags.",
      {"url": {"type": "string"}}, ["url"])
def summarize_jsonstat(ctx: ToolContext, args: dict) -> dict:
    dataset, _ = ctx.http.get_json(args["url"], max_bytes=5_000_000, agent=ctx.agent)
    return {"url": args["url"], **jsonstat_summary(dataset)}
