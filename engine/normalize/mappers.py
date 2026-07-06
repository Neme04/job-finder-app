"""Raw adapter records -> canonical Job. One function per source id.

Each source's raw shape is documented inline next to its mapper.
"""

import re
from datetime import datetime, timezone
from typing import Optional

from engine.models import Job
from engine.normalize.canonical import canonical_key, clean_apply_url

MAX_DESCRIPTION_LEN = 5000

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(html: Optional[str]) -> Optional[str]:
    if not html:
        return None
    text = _TAG_RE.sub(" ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_DESCRIPTION_LEN] if text else None


def _display_company(token: str) -> str:
    return token.replace("-", " ").replace("_", " ").title()


def _parse_iso(value) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, (int, float)):
        # epoch, seconds or milliseconds
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------- greenhouse
def _normalize_greenhouse(raw: dict) -> Job:
    company = _display_company(raw["_company_token"])
    title = raw.get("title", "")
    location = (raw.get("location") or {}).get("name")
    apply_url = clean_apply_url(raw.get("absolute_url", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="greenhouse",
        external_id=str(raw["id"]),
        title=title,
        company=company,
        location=location,
        remote="remote" in (location or "").lower(),
        description=_strip_html(raw.get("content")),
        apply_url=apply_url,
        posted_at=_parse_iso(raw.get("updated_at")),
        raw={"departments": raw.get("departments")},
    )


# ---------------------------------------------------------------- lever
def _normalize_lever(raw: dict) -> Job:
    company = _display_company(raw["_company_token"])
    title = raw.get("text", "")
    categories = raw.get("categories") or {}
    location = categories.get("location")
    apply_url = clean_apply_url(raw.get("applyUrl") or raw.get("hostedUrl", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="lever",
        external_id=str(raw["id"]),
        title=title,
        company=company,
        location=location,
        remote="remote" in (location or "").lower(),
        description=_strip_html(raw.get("descriptionPlain") or raw.get("description")),
        apply_url=apply_url,
        posted_at=_parse_iso(raw.get("createdAt")),
        raw={"team": categories.get("team"), "commitment": categories.get("commitment")},
    )


# ---------------------------------------------------------------- ashby
def _normalize_ashby(raw: dict) -> Job:
    company = _display_company(raw["_company_token"])
    title = raw.get("title", "")
    location = raw.get("location")
    apply_url = clean_apply_url(raw.get("applyUrl") or raw.get("jobUrl", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="ashby",
        external_id=str(raw["id"]),
        title=title,
        company=company,
        location=location,
        remote=bool(raw.get("isRemote", False)),
        description=_strip_html(raw.get("descriptionPlain") or raw.get("descriptionHtml")),
        apply_url=apply_url,
        posted_at=_parse_iso(raw.get("publishedAt")),
        raw={},
    )


# ---------------------------------------------------------------- remotive
def _normalize_remotive(raw: dict) -> Job:
    company = raw.get("company_name", "")
    title = raw.get("title", "")
    location = raw.get("candidate_required_location")
    apply_url = clean_apply_url(raw.get("url", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="remotive",
        external_id=str(raw["id"]),
        title=title,
        company=company,
        location=location,
        remote=True,
        description=_strip_html(raw.get("description")),
        apply_url=apply_url,
        currency=None,
        posted_at=_parse_iso(raw.get("publication_date")),
        raw={"tags": raw.get("tags"), "category": raw.get("category")},
    )


# ---------------------------------------------------------------- remoteok
def _normalize_remoteok(raw: dict) -> Job:
    company = raw.get("company", "")
    title = raw.get("position", "")
    location = raw.get("location")
    apply_url = clean_apply_url(raw.get("url", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="remoteok",
        external_id=str(raw.get("id", "")),
        title=title,
        company=company,
        location=location,
        remote=True,
        description=_strip_html(raw.get("description")),
        apply_url=apply_url,
        salary_min=raw.get("salary_min"),
        salary_max=raw.get("salary_max"),
        posted_at=_parse_iso(raw.get("date")),
        raw={"tags": raw.get("tags")},
    )


# ---------------------------------------------------------------- arbeitnow
def _normalize_arbeitnow(raw: dict) -> Job:
    company = raw.get("company_name", "")
    title = raw.get("title", "")
    location = raw.get("location")
    apply_url = clean_apply_url(raw.get("url", ""))
    return Job(
        canonical_key=canonical_key(company, title, location),
        source_id="arbeitnow",
        external_id=str(raw.get("slug", "")),
        title=title,
        company=company,
        location=location,
        remote=bool(raw.get("remote", False)),
        description=_strip_html(raw.get("description")),
        apply_url=apply_url,
        posted_at=_parse_iso(raw.get("created_at")),
        raw={"tags": raw.get("tags"), "job_types": raw.get("job_types")},
    )


_NORMALIZERS = {
    "greenhouse": _normalize_greenhouse,
    "lever": _normalize_lever,
    "ashby": _normalize_ashby,
    "remotive": _normalize_remotive,
    "remoteok": _normalize_remoteok,
    "arbeitnow": _normalize_arbeitnow,
}


def normalize_records(source_id: str, raw_records: list[dict]) -> list[Job]:
    normalizer = _NORMALIZERS.get(source_id)
    if normalizer is None:
        raise NotImplementedError(f"No normalizer registered for '{source_id}'")

    jobs = []
    for raw in raw_records:
        try:
            jobs.append(normalizer(raw))
        except (KeyError, TypeError):
            continue
    return jobs
