"""Licence and structured-metadata extraction from dataset landing pages."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser


def jsonld_datasets(html: str) -> list[dict]:
    """Return every schema.org Dataset object embedded as JSON-LD in a page.

    Many portals (Kaggle, Zenodo, data.gov, Hugging Face, Dataverse, CKAN sites) embed one.
    It is the most reliable machine-readable description of a dataset when it exists.
    """
    found = []
    for m in re.finditer(r"""(?is)<script[^>]*type=["']application/ld\+json["'][^>]*>(.*?)</script>""", html):
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        for item in items:
            if isinstance(item, dict) and "Dataset" in str(item.get("@type", "")):
                found.append(item)
    return found


def summarise_jsonld_dataset(d: dict) -> dict:
    """Keep the fields that matter for discovery, clipped for the model."""
    def name_of(v):
        if isinstance(v, list):
            return [name_of(x) for x in v][:5]
        if isinstance(v, dict):
            return v.get("name") or v.get("url") or v.get("@id")
        return v

    def clip(v, n=600):
        v = re.sub(r"<[^>]+>", " ", str(v)) if v is not None else None
        return None if v is None else (" ".join(v.split())[:n])

    dist = d.get("distribution") or []
    dist = dist if isinstance(dist, list) else [dist]
    return {
        "name": d.get("name"), "description": clip(d.get("description")),
        "license": d.get("license"), "creator": name_of(d.get("creator")), "publisher": name_of(d.get("publisher")),
        "datePublished": d.get("datePublished"), "dateModified": d.get("dateModified"),
        "temporalCoverage": d.get("temporalCoverage"), "spatialCoverage": name_of(d.get("spatialCoverage")),
        "isAccessibleForFree": d.get("isAccessibleForFree"), "keywords": clip(d.get("keywords"), 300),
        "variableMeasured": name_of(d.get("variableMeasured")),
        "distribution": [{k: x.get(k) for k in ("contentUrl", "encodingFormat", "fileFormat", "contentSize", "requiresSubscription", "name")
                          if isinstance(x, dict) and x.get(k) is not None} for x in dist[:10]],
    }


# ---------------------------------------------------------------------------
# G1: find the licence of ANY dataset from its landing page
# ---------------------------------------------------------------------------
# Contract (tests/test_learner_gaps.py::test_g1_* checks it):
#   extract_licence(html: str, jsonld: list[dict] | None = None) -> dict with EXACTLY these keys
#     licence_name : normalised name, one of e.g. "CC BY 4.0", "CC BY-SA 4.0", "CC BY-NC 4.0", "CC BY-NC-SA 4.0",
#                    "CC BY-ND 4.0", "CC0 1.0", "ODbL 1.0", "OGL v3.0", "MIT", "Apache-2.0"; None if not found
#                    or if the page says the licence is unknown/unspecified
#     licence_url  : the licence URL you found, or None
#     snippet      : the text or JSON-LD value you read it from (<= 400 chars), or None
#     found_in     : "json-ld" | "link" | "text" | None
#
# Order of evidence: JSON-LD "license" (string URL, or {"name", "url"}) first; then links to
# creativecommons.org / opendatacommons.org / nationalarchives.gov.uk (OGL) / choosealicense.com;
# then sentences such as "licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license".
# jsonld defaults to jsonld_datasets(html) when None. Never guess: return None values when unsure.
_SNIPPET_MAX = 400


def extract_licence(html: str, jsonld: list[dict] | None = None) -> dict:
    """Return the dataset's licence as {licence_name, licence_url, snippet, found_in}.

    Three kinds of evidence, strongest first. The first kind the page has decides, and the search stops there:
      1. "json-ld": the license/licence field of the page's schema.org Dataset. A stated value is final even when
         it is not a licence we recognise (Kaggle's "Unknown"): the name is None and the raw value is the snippet.
      2. "link": links in the page content whose target is a licence's legal text. The URL names the licence.
      3. "text": sentences in the page content that name a licence ("licensed under CC BY 4.0").
    The page content excludes <header>, <nav> and <footer>: a licence there is usually the website's own.
    Within one kind, all the evidence must agree on one licence; otherwise the name is None (dual licence,
    BY vs BY-NC, 3.0 vs 4.0). Wording we do not recognise also gives None, never the raw string, because
    risk_rules.rule_licence only reads a few words as unknown: a raw "Not specified" would raise no flag.
    It never raises: odd input gives the all-None result.
    """
    html = html if isinstance(html, str) else ""
    if jsonld is None:  # [] means the caller found no JSON-LD (the UCI path): do not parse again
        jsonld = jsonld_datasets(html)
    found = _decide("json-ld", _jsonld_evidence(jsonld if isinstance(jsonld, list) else []))
    if found is None:
        blocks, links = _read_page(html)
        found = _decide("link", _link_evidence(blocks, links)) or _decide("text", _text_evidence(blocks))
    return found or _result()


def _result(name: str | None = None, url: str | None = None, snippet: str | None = None, found_in: str | None = None) -> dict:
    return {"licence_name": name, "licence_url": url, "snippet": snippet[:_SNIPPET_MAX] if snippet else None, "found_in": found_in}


# Evidence is a list of (licence name or None, URL or None, snippet). None as a name means
# "a licence statement we cannot read"; only JSON-LD produces it.
def _decide(found_in: str, evidence: list[tuple[str | None, str | None, str]]) -> dict | None:
    """Turn the evidence of one kind into a result, or None when the page has no evidence of that kind."""
    if not evidence:
        return None
    names = {name for name, _, _ in evidence}
    # A versionless name agrees with the same licence stated with a version: "CC BY" + "CC BY 4.0" -> "CC BY 4.0".
    names -= {n for n in names if n and any(m and m.startswith(n + " ") for m in names)}
    if len(names) == 1 and None not in names:
        name = names.pop()
        url = next((u for n, u, _ in evidence if n == name and u), None)
        snippet = next(s for n, _, s in evidence if n == name)
        return _result(name, url, snippet, found_in)
    urls = {u for _, u, _ in evidence if u}  # several licences, or one we cannot read: keep the URL only if there is one
    return _result(None, urls.pop() if len(urls) == 1 else None, " | ".join(dict.fromkeys(s for _, _, s in evidence)), found_in)


# -- 1. JSON-LD ---------------------------------------------------------------------
_LICENCE_KEY = re.compile(r"(?:.*[:/#])?licen[cs]e", re.I)  # license, licence, dct:license, http://schema.org/license
_URL_START = re.compile(r"(?:https?:)?//|www\.", re.I)


def _jsonld_evidence(datasets: list) -> list[tuple]:
    evidence = []
    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue
        for key, value in dataset.items():
            if not (isinstance(key, str) and _LICENCE_KEY.fullmatch(key)):
                continue
            for item in value if isinstance(value, list) else [value]:
                url, labels = _statement(item)
                if not url and not labels:
                    continue  # an empty value ("", {}, {"name": "", "url": ""}) counts as absent
                found = ([_name_from_url(url)] if url else []) + [n for label in labels for n in _names_in_label(label)]
                names = list(dict.fromkeys(n for n in found if n)) or [None]
                snippet = json.dumps({key: item}, ensure_ascii=False, default=str)
                evidence += [(name, url, snippet) for name in names]
    return evidence


def _statement(item) -> tuple[str | None, list[str]]:
    """Split one JSON-LD licence value into (URL or None, labels). A string is a URL only if it starts like one."""
    if isinstance(item, str):
        text = item.strip()
        return (text, []) if _URL_START.match(text) else (None, [text] if text else [])
    if isinstance(item, dict):  # e.g. {"@type": "CreativeWork", "name": "CC BY-NC-SA 4.0", "url": ""}
        urls = [s for k in ("url", "@id", "sameAs") for s in _strings(item.get(k)) if _URL_START.match(s)]
        labels = [s for k in ("name", "alternateName", "identifier") for s in _strings(item.get(k))]
        return (urls[0] if urls else None), labels
    return None, []  # a number, boolean or null is not a licence statement


def _strings(value) -> list[str]:
    """The non-empty strings in a JSON-LD field that holds a string or a list."""
    return [v.strip() for v in (value if isinstance(value, list) else [value]) if isinstance(v, str) and v.strip()]


# -- 2. links and 3. text in the page content ------------------------------------------
def _link_evidence(blocks: list[str], links: list[tuple[str, str, int]]) -> list[tuple]:
    evidence = []
    for href, text, block in links:
        name = _name_from_url(href)
        if name:
            evidence.append((name, href, _context(blocks, block) or text or href))
    return evidence


def _text_evidence(blocks: list[str]) -> list[tuple]:
    evidence = []
    for i, block in enumerate(blocks):
        for sentence in re.split(r"(?<=[.!?])\s+", block):
            for name in _names_in_text(sentence):
                evidence.append((name, None, _context(blocks, i) if sentence == block else sentence))
    return evidence


def _context(blocks: list[str], i: int) -> str:
    """Block i of the page text; a very short block ("Read more", a table cell) gets the block before it, often its label."""
    if not 0 <= i < len(blocks):
        return ""
    return f"{blocks[i - 1]} {blocks[i]}" if len(blocks[i]) < 40 and i > 0 else blocks[i]


# -- licence names: pattern rules, never a list of known pages -----------------------
_CC_VERSION = r"(1\.0|2\.0|2\.5|3\.0|4\.0)"  # the versions Creative Commons has published; any other number is ignored


def _cc_name(modifiers: set[str], version: str | None) -> str:
    """Build "CC BY" + the modifiers in the official order (NC, ND, SA) + the version, only when one was stated."""
    tags = "".join(f"-{code.upper()}" for code in ("nc", "nd", "sa") if code in modifiers)
    return f"CC BY{tags} {version}" if version else f"CC BY{tags}"


def _cc_abbreviated(m: re.Match) -> str:  # "CC BY-NC-SA 4.0", "cc-by-4.0"
    return _cc_name(set(re.findall(r"nc|nd|sa", m.group(1).lower())), m.group(2))


def _cc_spelled_out(m: re.Match) -> str:  # "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"
    words = m.group(1).lower()
    return _cc_name({code for code, word in (("nc", "commercial"), ("nd", "deriv"), ("sa", "alike")) if word in words}, m.group(2))


def _ogl(m: re.Match) -> str:
    return f"OGL v{m.group(1)}.0" if m.group(1) else "OGL"


_TEXT_RULES = [(re.compile(pattern, re.I), name_of) for pattern, name_of in [
    # Creative Commons BY family, abbreviated or spelled out. No version stated -> none is added ("CC BY").
    (rf"\bcc[- ]?by((?:[- ](?:nc|nd|sa)\b)*)(?:[- ]?v?{_CC_VERSION})?\b", _cc_abbreviated),
    (r"\bcreative\s+commons\s+attribution((?:[\s\-–]+(?:non[\s-]?commercial|no[\s-]?deriv(?:ative)?s|share[\s-]?alike))*)"
     rf"(?:[\s,]+(?:licen[cs]e[\s,]*)?(?:version\s*|v\.?\s*)?{_CC_VERSION})?", _cc_spelled_out),
    # Public-domain dedications and Open Data Commons licences: each exists only as version 1.0.
    (r"\bcc-?0\b|\bcc[\s-]?zero\b|\bcreative\s+commons\s+zero\b", lambda m: "CC0 1.0"),
    (r"\bodbl\b|\bopen\s+database\s+licen[cs]e\b", lambda m: "ODbL 1.0"),
    (r"\bodc[\s-]?by\b|\bopen\s+data\s+commons\s+attribution\b", lambda m: "ODC-By 1.0"),
    (r"\bpddl\b|\bpublic\s+domain\s+dedication\s+and\s+licen[cs]e\b", lambda m: "PDDL 1.0"),
    # UK Open Government Licence. "Open Government Licence – Canada" (or a province) is a different licence.
    (r"\bopen\s+government\s+licen[cs]e(?!\s*[-–—]\s*(?!uk\b|v(?:ersion)?[\s.]*\d)[a-z])(?:\s+for\s+public\s+sector\s+information)?"
     r"(?:\s*\(ogl\))?(?:[\s,\-–]*(?:version|v)\.?\s*([1-3])(?:\.0)?\b)?", _ogl),
    (r"\bogl[\s-]?(?:uk[\s-]?)?v?([1-3])(?:\.0)?\b", _ogl),
    # Software licences: "MIT" only next to the word licence ("researchers at MIT" is not a licence);
    # "Apache" only followed by version 2.0 or 2-0 ("Apache Spark" is a product).
    (r"\bmit[\s-]+licen[cs]ed?\b|\blicen[cs]ed\s+under\s+(?:the\s+)?mit\b", lambda m: "MIT"),
    (r"\bapache(?:[\s-]+licen[cs]e)?[\s,-]*(?:version\s*|v\.?\s*)?2[.-]0\b", lambda m: "Apache-2.0"),
]]


def _names_in_text(text: str) -> list[str]:
    """Every licence named in a piece of text, in order of appearance, without repeats."""
    found = sorted((m.start(), name_of(m)) for pattern, name_of in _TEXT_RULES for m in pattern.finditer(text))
    return list(dict.fromkeys(name for _, name in found))


def _names_in_label(label: str) -> list[str]:
    """Like _names_in_text, for a short label or licence id (a JSON-LD name, a registry URL slug), where "MIT" alone is the id."""
    return _names_in_text(label) or (["MIT"] if label.strip().lower() == "mit" else [])


_REGISTRY_SLUG = re.compile(r"(?:choosealicense\.com|spdx\.org|opensource\.org|opendefinition\.org)/licenses?/([^/]+)")


def _name_from_url(url: str) -> str | None:
    """The licence a URL points to, judged by the URL patterns of the licence publishers; None for any other URL."""
    u = re.sub(r"^(?:https?:)?//", "", url.strip().lower())
    u = re.split(r"[?#]", re.sub(r"^www\.", "", u), maxsplit=1)[0]
    if m := re.match(rf"creativecommons\.org/licenses/by((?:-(?:nc|nd|sa))*)(?:/{_CC_VERSION})?(?:/|$)", u):
        return _cc_name(set(re.findall(r"nc|nd|sa", m.group(1))), m.group(2))
    if re.match(r"creativecommons\.org/publicdomain/zero(?:/|$)", u):
        return "CC0 1.0"
    if m := re.match(r"opendatacommons\.org/licenses/(odbl|by|pddl)(?:/|$)", u):
        return {"odbl": "ODbL 1.0", "by": "ODC-By 1.0", "pddl": "PDDL 1.0"}[m.group(1)]
    if m := re.match(r"nationalarchives\.gov\.uk/doc/open-government-licen[cs]e(?:/version/([1-3]))?(?:/|$)", u):
        return _ogl(m)
    if re.match(r"apache\.org/licenses/license-2\.0", u):
        return "Apache-2.0"
    if m := _REGISTRY_SLUG.match(u):  # licence registries name the licence by its id: cc0-1.0, cc-by-4.0, mit
        names = _names_in_label(re.sub(r"\.(?:html?|json|txt)$", "", m.group(1)))
        return names[0] if len(names) == 1 else None
    return None


# -- reading the page content -------------------------------------------------------
_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "title",  # not visible text
              "header", "nav", "footer"}  # site chrome; <aside> is kept: some portals put the dataset's rights box there
_BLOCK_TAGS = {"p", "div", "li", "dt", "dd", "td", "th", "tr", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "section",
               "article", "aside", "main", "ul", "ol", "dl", "table", "blockquote", "pre", "figure", "figcaption", "body"}


def _read_page(html: str) -> tuple[list[str], list[tuple[str, str, int]]]:
    """The page content as text blocks, plus its links as (href, link text, index of the block holding the link)."""
    reader = _PageReader()
    try:
        reader.feed(html)
        reader.close()
    except AssertionError:  # html.parser raises this on malformed "<![...]>" markup (Python 3.12); keep what was read
        pass
    reader.finish()
    return reader.blocks, reader.links


class _PageReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.links: list[tuple[str, str, int]] = []
        self._skip = 0  # depth inside _SKIP_TAGS elements
        self._text: list[str] = []  # text of the block being read
        self._link: tuple[str, list[str], int] | None = None  # the open <a>: href, its text, its block index

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip += 1
        elif self._skip:
            return
        elif tag == "a":
            self._end_link()
            href = dict(attrs).get("href")
            if href and href.strip():
                self._link = (href.strip(), [], len(self.blocks))
        elif tag in _BLOCK_TAGS:
            self._end_block()

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif self._skip:
            return
        elif tag == "a":
            self._end_link()
        elif tag in _BLOCK_TAGS:
            self._end_block()

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)
            if self._link:
                self._link[1].append(data)

    def finish(self):
        self._end_link()
        self._end_block()

    def _end_link(self):
        if self._link:
            href, text, block = self._link
            self.links.append((href, " ".join("".join(text).split()), block))
            self._link = None

    def _end_block(self):
        text = " ".join("".join(self._text).split())
        if text:
            self.blocks.append(text)
        self._text = []
