"""Admin-only WhatsApp alerts via CallMeBot.

CallMeBot is personal-use: it only ever messages the admin's own
authorized number, using server-side secrets never collected from users.
Per CLAUDE.md §7, this path must never run for non-admin profiles.
"""

import os

import requests

from engine.http import request_with_retry

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"
REQUEST_TIMEOUT = 15
MAX_TITLES_SHOWN = 5


class CallMeBotNotConfigured(requests.RequestException):
    """Raised instead of KeyError so callers can catch it alongside network
    errors — an admin can flip the WhatsApp toggle before the secrets are
    set, and that shouldn't crash the whole notify step."""


def build_whatsapp_summary(jobs: list[dict], feed_url: str) -> str:
    count = len(jobs)
    noun = "match" if count == 1 else "matches"
    lines = [f"🔔 {count} new job {noun}:"]
    for job in jobs[:MAX_TITLES_SHOWN]:
        lines.append(f"- {job['title']} @ {job['company']}")
    remaining = count - MAX_TITLES_SHOWN
    if remaining > 0:
        lines.append(f"...+{remaining} more")
    lines.append(f"View all: {feed_url}")
    return "\n".join(lines)


def send_whatsapp_message(text: str) -> None:
    phone = os.environ.get("CALLMEBOT_PHONE")
    apikey = os.environ.get("CALLMEBOT_APIKEY")
    if not phone or not apikey:
        raise CallMeBotNotConfigured("CALLMEBOT_PHONE/CALLMEBOT_APIKEY not set")
    request_with_retry(
        "get",
        CALLMEBOT_URL,
        params={"phone": phone, "text": text, "apikey": apikey},
        timeout=REQUEST_TIMEOUT,
    )
