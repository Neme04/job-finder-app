"""Turns the shared jobs pool into per-user matches (`user_jobs`), per CLAUDE.md §5.

Missing salary data is treated as "unknown" and passes the salary filter rather
than failing it — most postings don't carry salary info (BUILD-PLAN.md Phase 2).
Matching runs against the full jobs pool each time; inserts are idempotent via
an ignore-duplicates upsert on (profile_id, job_id), so re-running the matcher
never re-inserts or overwrites a user's existing status on a job.
"""

import os

import requests

REQUEST_TIMEOUT = 30
BATCH_SIZE = 500


def _client_config() -> tuple[str, str]:
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, key


def _headers(key: str, prefer: str) -> dict:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def load_search_criteria() -> list[dict]:
    url, key = _client_config()
    resp = requests.get(
        f"{url}/rest/v1/search_criteria",
        headers=_headers(key, prefer=""),
        params={"select": "*"},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def load_jobs() -> list[dict]:
    url, key = _client_config()
    resp = requests.get(
        f"{url}/rest/v1/jobs",
        headers=_headers(key, prefer=""),
        params={
            "select": "id,source_id,title,company,location,remote,salary_min,salary_max"
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _title_matches(criteria: dict, job: dict) -> bool:
    titles = criteria.get("job_titles") or []
    if not titles:
        return True
    job_title = (job.get("title") or "").lower()
    return any(t.lower() in job_title for t in titles)


def _region_matches(criteria: dict, job: dict) -> bool:
    regions = criteria.get("regions") or []
    if not regions:
        return True
    if job.get("remote"):
        return True
    location = (job.get("location") or "").lower()
    return any(r.lower() in location for r in regions)


def _remote_pref_matches(criteria: dict, job: dict) -> bool:
    remote_pref = criteria.get("remote_pref")
    if remote_pref == "remote":
        return bool(job.get("remote"))
    return True


def _salary_matches(criteria: dict, job: dict) -> bool:
    floor = criteria.get("salary_floor")
    if floor is None:
        return True
    job_salary = job.get("salary_max") or job.get("salary_min")
    if job_salary is None:
        return True  # unknown salary passes, per BUILD-PLAN.md Phase 2
    return job_salary >= floor


def _source_matches(criteria: dict, job: dict) -> bool:
    sources = criteria.get("sources_enabled") or []
    if not sources:
        return True
    return job.get("source_id") in sources


def matches(criteria: dict, job: dict) -> bool:
    return (
        _title_matches(criteria, job)
        and _region_matches(criteria, job)
        and _remote_pref_matches(criteria, job)
        and _salary_matches(criteria, job)
        and _source_matches(criteria, job)
    )


def build_user_job_rows(criteria_rows: list[dict], jobs: list[dict]) -> list[dict]:
    rows = []
    for criteria in criteria_rows:
        profile_id = criteria["profile_id"]
        for job in jobs:
            if matches(criteria, job):
                rows.append({"profile_id": profile_id, "job_id": job["id"], "status": "new"})
    return rows


def insert_user_job_matches(rows: list[dict]) -> int:
    if not rows:
        return 0

    url, key = _client_config()
    endpoint = f"{url}/rest/v1/user_jobs?on_conflict=profile_id,job_id"
    headers = _headers(key, prefer="resolution=ignore-duplicates,return=minimal")

    written = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        resp = requests.post(endpoint, headers=headers, json=batch, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        written += len(batch)
    return written


def run_matcher() -> int:
    criteria_rows = load_search_criteria()
    jobs = load_jobs()
    rows = build_user_job_rows(criteria_rows, jobs)
    return insert_user_job_matches(rows)
