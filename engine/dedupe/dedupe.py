"""In-run dedupe across sources, per job-sources-config.md §Dedupe.

Cross-run seen-set persistence (first_seen/last_seen, expiry) happens in the
writer against Supabase, not here — this only collapses duplicates produced
by a single sweep.
"""

from difflib import SequenceMatcher

from engine.models import Job

# lower number = preferred when the same canonical_key appears from multiple
# sources (matches each source's "priority" field in sources.config.json —
# direct ATS/company sources rank above aggregators/feeds).
_SOURCE_RANK = {
    "greenhouse": 1,
    "lever": 1,
    "ashby": 1,
    "remotive": 2,
    "arbeitnow": 2,
    "remoteok": 2,
}

FUZZY_MATCH_THRESHOLD = 0.9


def _rank(job: Job) -> int:
    return _SOURCE_RANK.get(job.source_id, 99)


def _fuzzy_key(job: Job) -> str:
    return f"{job.title} {job.company}".lower()


def dedupe_jobs(jobs: list[Job]) -> list[Job]:
    # exact canonical_key collisions: keep the highest-ranked (most direct) source
    best_by_key: dict[str, Job] = {}
    for job in jobs:
        existing = best_by_key.get(job.canonical_key)
        if existing is None or _rank(job) < _rank(existing):
            best_by_key[job.canonical_key] = job

    deduped = list(best_by_key.values())

    # fuzzy near-dupes across differing canonical keys (e.g. "Sr. Designer" vs "Senior Designer, Product")
    # grouped by company first so the pairwise comparison only runs within same-company batches
    by_company: dict[str, list[Job]] = {}
    for job in deduped:
        by_company.setdefault(job.company.lower(), []).append(job)

    kept: list[Job] = []
    for company_jobs in by_company.values():
        company_kept: list[Job] = []
        for job in company_jobs:
            job_fuzzy = _fuzzy_key(job)
            is_dupe = False
            for i, existing in enumerate(company_kept):
                ratio = SequenceMatcher(None, job_fuzzy, _fuzzy_key(existing)).ratio()
                if ratio >= FUZZY_MATCH_THRESHOLD:
                    is_dupe = True
                    if _rank(job) < _rank(existing):
                        company_kept[i] = job
                    break
            if not is_dupe:
                company_kept.append(job)
        kept.extend(company_kept)

    return kept
