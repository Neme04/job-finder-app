"""Resend digest email: one email per user per sweep run, never per job.

Uses Resend's HTTP API directly (no SDK dependency).
"""

import os

import requests

RESEND_API_URL = "https://api.resend.com/emails"
REQUEST_TIMEOUT = 15


def _from_address() -> str:
    return os.environ.get("RESEND_FROM", "Job Finder <onboarding@resend.dev>")


def build_digest_html(jobs: list[dict], feed_url: str, settings_url: str) -> str:
    count = len(jobs)
    noun = "match" if count == 1 else "matches"
    items = "".join(
        "<li style=\"margin-bottom:8px\">"
        f"<strong>{job['title']}</strong> at {job['company']}"
        + (f" &middot; {job['location']}" if job.get("location") else "")
        + "</li>"
        for job in jobs
    )
    return f"""
    <div style="font-family:system-ui,sans-serif;color:#181818;max-width:520px">
      <p>You have {count} new job {noun}:</p>
      <ul style="padding-left:20px">{items}</ul>
      <p><a href="{feed_url}" style="color:#7f56d9">View in Job Finder</a></p>
      <p style="color:#888;font-size:12px;margin-top:24px">
        Manage notification preferences in
        <a href="{settings_url}" style="color:#888">Settings</a>.
      </p>
    </div>
    """


def send_digest_email(to_email: str, jobs: list[dict], feed_url: str, settings_url: str) -> None:
    api_key = os.environ["RESEND_API_KEY"]
    count = len(jobs)
    subject = f"{count} new job {'match' if count == 1 else 'matches'} on Job Finder"

    resp = requests.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "from": _from_address(),
            "to": [to_email],
            "subject": subject,
            "html": build_digest_html(jobs, feed_url, settings_url),
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
