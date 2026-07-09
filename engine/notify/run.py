"""Wires the matcher's output to Resend digest emails.

One digest per user per run, only for rows not yet notified
(user_jobs.notified_at IS NULL), only for profiles with notify_email=true.
Stays under Resend's free-tier ~100/day cap with a safety margin.
"""

import os
from collections import defaultdict
from datetime import datetime, timezone

import requests

from engine.http import request_with_retry
from engine.notify.email import send_digest_email

REQUEST_TIMEOUT = 30
DAILY_SAFETY_CAP = 90  # headroom under Resend's 100/day free-tier limit
PAGE_SIZE = 1000  # Supabase's default max rows per request


def _client_config() -> tuple[str, str]:
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return url, key


def _headers(key: str, prefer: str = "") -> dict:
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _load_pending_notifications() -> dict[str, list[dict]]:
    """profile_id -> list of {id, title, company, location} for unnotified new matches."""
    url, key = _client_config()

    all_rows: list[dict] = []
    for page in range(20):
        headers = {
            **_headers(key),
            "Range": f"{page * PAGE_SIZE}-{page * PAGE_SIZE + PAGE_SIZE - 1}",
        }
        resp = request_with_retry(
            "get",
            f"{url}/rest/v1/user_jobs",
            headers=headers,
            params={
                "select": "id,profile_id,jobs(title,company,location),profiles!inner(notify_email)",
                "notified_at": "is.null",
                "status": "eq.new",
                "profiles.notify_email": "eq.true",
            },
            timeout=REQUEST_TIMEOUT,
        )
        batch = resp.json()
        all_rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break

    by_profile: dict[str, list[dict]] = defaultdict(list)
    for row in all_rows:
        job = row["jobs"]
        by_profile[row["profile_id"]].append(
            {
                "user_job_id": row["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job.get("location"),
            }
        )
    return by_profile


def _get_user_email(user_id: str) -> str | None:
    url, key = _client_config()
    resp = requests.get(
        f"{url}/auth/v1/admin/users/{user_id}",
        headers=_headers(key),
        timeout=REQUEST_TIMEOUT,
    )
    if resp.status_code != 200:
        return None
    return resp.json().get("email")


def _mark_notified(user_job_ids: list[str]) -> None:
    url, key = _client_config()
    now_iso = datetime.now(timezone.utc).isoformat()
    ids = ",".join(user_job_ids)
    request_with_retry(
        "patch",
        f"{url}/rest/v1/user_jobs",
        headers=_headers(key, prefer="return=minimal"),
        params={"id": f"in.({ids})"},
        json={"notified_at": now_iso},
        timeout=REQUEST_TIMEOUT,
    )


def run_email_notify() -> int:
    """Returns the number of digest emails sent."""
    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    feed_url = f"{frontend_url}/feed"
    settings_url = f"{frontend_url}/settings"

    pending = _load_pending_notifications()
    sent = 0

    for profile_id, jobs in pending.items():
        if sent >= DAILY_SAFETY_CAP:
            print(f"[notify] hit daily safety cap ({DAILY_SAFETY_CAP}), stopping early")
            break

        email = _get_user_email(profile_id)
        if not email:
            continue

        digest_jobs = [{"title": j["title"], "company": j["company"], "location": j["location"]} for j in jobs]
        try:
            send_digest_email(email, digest_jobs, feed_url, settings_url)
        except requests.RequestException as e:
            print(f"[notify] failed to send digest to {email}: {e}")
            continue

        _mark_notified([j["user_job_id"] for j in jobs])
        sent += 1

    return sent
