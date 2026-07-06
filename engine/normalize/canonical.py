"""Canonical key + apply-URL cleanup shared by every normalizer.

Per job-sources-config.md §Dedupe:
canonical_key = normalize(company) :: normalize(title) :: normalize(location)
"""

import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")

_SENIORITY_FILLER = {
    "senior", "sr", "junior", "jr", "lead", "staff", "principal",
    "i", "ii", "iii", "iv",
}

_TRACKING_PARAM_PREFIXES = ("utm_", "gh_src", "ref", "trk", "source")


def _normalize_token_string(value: str) -> str:
    value = value.lower().strip()
    value = _PUNCT_RE.sub("", value)
    value = _WS_RE.sub(" ", value).strip()
    tokens = [t for t in value.split(" ") if t not in _SENIORITY_FILLER]
    return " ".join(tokens)


def normalize(value: str | None) -> str:
    if not value:
        return ""
    return _normalize_token_string(value)


def canonical_key(company: str, title: str, location: str | None) -> str:
    return "::".join([normalize(company), normalize(title), normalize(location)])


def clean_apply_url(url: str) -> str:
    """Strip tracking query params from an apply URL."""
    if not url:
        return url
    parts = urlsplit(url)
    kept = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not any(k.lower().startswith(p) for p in _TRACKING_PARAM_PREFIXES)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), ""))
