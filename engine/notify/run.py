"""Wires the matcher's output to per-user notifications: email (everyone who
opts in) and WhatsApp (admin only, per CLAUDE.md §7).

One notification pass per user per run, only for rows not yet notified
(user_jobs.notified_at IS NULL). A user's pending matches aren't gated on
any single channel's toggle — an admin could have email off but WhatsApp
on — so the query fetches all pending rows and each channel decides for
itself whether to fire, based on the embedded profile flags. notified_at
is marked once at least one channel actually sends, so a completely
opted-out user is left pending indefinitely (harmless — it only affects
notifications, not feed visibility) rather than silently marked "notified"
with nothing sent.
"""

import os
from collections import defaultdict
from datetime import datetime, timezone

import requests

from engine.http import request_with_retry
from engine.notify.email import send_digest_email
from engine.notify.whatsapp import build_whatsapp_summary, send_whatsapp_message

REQUEST_TIMEOUT = 30
EMAIL_DAILY_SAFETY_CAP = 90  # headroom under Resend's 100/day free-tier limit
WHATSAPP_DAILY_SAFETY_CAP = 90  # single admin recipient; generous headroom regardless
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


def _load_pending_notifications() -> dict[str, dict]:
    """profile_id -> {notify_email, notify_whatsapp, role, jobs: [...]}."""
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
                "select": "id,profile_id,jobs(title,company,location),profiles(notify_email,notify_whatsapp,role)",
                "notified_at": "is.null",
                "status": "eq.new",
                # Stable order required for correct pagination (see matcher.load_jobs).
                "order": "id",
            },
            timeout=REQUEST_TIMEOUT,
        )
        batch = resp.json()
        all_rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break

    by_profile: dict[str, dict] = {}
    for row in all_rows:
        profile_id = row["profile_id"]
        profile = row["profiles"]
        job = row["jobs"]
        entry = by_profile.setdefault(
            profile_id,
            {
                "notify_email": profile["notify_email"],
                "notify_whatsapp": profile["notify_whatsapp"],
                "role": profile["role"],
                "jobs": [],
            },
        )
        entry["jobs"].append(
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


def run_notifications() -> dict[str, int]:
    """Returns {"email": count, "whatsapp": count} of notifications sent."""
    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    feed_url = f"{frontend_url}/feed"
    settings_url = f"{frontend_url}/settings"

    pending = _load_pending_notifications()
    email_sent = 0
    whatsapp_sent = 0

    for profile_id, entry in pending.items():
        jobs = entry["jobs"]
        digest_jobs = [
            {"title": j["title"], "company": j["company"], "location": j["location"]} for j in jobs
        ]

        wants_email = entry["notify_email"]
        # WhatsApp is admin-only, guarded on role, never on a user-supplied flag alone.
        wants_whatsapp = entry["role"] == "admin" and entry["notify_whatsapp"]

        if not wants_email and not wants_whatsapp:
            continue  # leave pending; nothing to notify through

        notified = False

        if wants_email and email_sent < EMAIL_DAILY_SAFETY_CAP:
            email = _get_user_email(profile_id)
            if email:
                try:
                    send_digest_email(email, digest_jobs, feed_url, settings_url)
                    email_sent += 1
                    notified = True
                except requests.RequestException as e:
                    print(f"[notify] failed to send email digest to {email}: {e}")
        elif wants_email:
            print(f"[notify] hit email daily safety cap ({EMAIL_DAILY_SAFETY_CAP})")

        if wants_whatsapp and whatsapp_sent < WHATSAPP_DAILY_SAFETY_CAP:
            try:
                summary = build_whatsapp_summary(digest_jobs, feed_url)
                send_whatsapp_message(summary)
                whatsapp_sent += 1
                notified = True
            except requests.RequestException as e:
                print(f"[notify] failed to send WhatsApp summary: {e}")
        elif wants_whatsapp:
            print(f"[notify] hit WhatsApp daily safety cap ({WHATSAPP_DAILY_SAFETY_CAP})")

        if notified:
            _mark_notified([j["user_job_id"] for j in jobs])

    return {"email": email_sent, "whatsapp": whatsapp_sent}
