"""Shared HTTP helper: retries transient network/SSL errors with backoff.

Supabase REST calls from this environment have intermittently hit
SSLEOFError on large POST bodies — not a code bug, just a flaky
connection. A few retries with backoff clears it.
"""

import time

import requests

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 2


def request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"[http] {method.upper()} {url} attempt {attempt}/{MAX_ATTEMPTS} failed: {e}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_SECONDS * attempt)
    raise last_error
