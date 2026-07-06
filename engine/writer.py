"""Upserts normalized jobs into Supabase's `jobs` table via the service key.

Uses the PostgREST HTTP API directly (no supabase-py dependency needed).
Upsert is keyed on the (source_id, external_id) unique constraint: `last_seen`
is refreshed on every run, `first_seen` is left untouched by omitting it from
the payload (its column default only applies on insert).
"""

import os
from datetime import datetime, timedelta, timezone

import requests

from engine.models import Job

BATCH_SIZE = 500
EXPIRE_AFTER_DAYS = 14


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


def _job_payload(job: Job, now_iso: str) -> dict:
    return {
        "canonical_key": job.canonical_key,
        "source_id": job.source_id,
        "external_id": job.external_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote": job.remote,
        "description": job.description,
        "apply_url": job.apply_url,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.currency,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
        "last_seen": now_iso,
    }


def upsert_jobs(jobs: list[Job]) -> int:
    if not jobs:
        return 0

    url, key = _client_config()
    now_iso = datetime.now(timezone.utc).isoformat()
    endpoint = f"{url}/rest/v1/jobs?on_conflict=source_id,external_id"
    headers = _headers(key, prefer="resolution=merge-duplicates,return=minimal")

    written = 0
    for i in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[i : i + BATCH_SIZE]
        payload = [_job_payload(j, now_iso) for j in batch]
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        written += len(batch)
    return written


def expire_stale_jobs(days: int = EXPIRE_AFTER_DAYS) -> None:
    url, key = _client_config()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    endpoint = f"{url}/rest/v1/jobs"
    headers = _headers(key, prefer="return=minimal")
    resp = requests.delete(
        endpoint, headers=headers, params={"last_seen": f"lt.{cutoff}"}, timeout=30
    )
    resp.raise_for_status()
