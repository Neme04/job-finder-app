"""Generic feed adapter for open, keyless job feeds (Remotive, RemoteOK, Arbeitnow, ...).

Fetch is pure: given a registry entry, return raw records. No normalization here.
"""

import requests

REQUEST_TIMEOUT = 15


def fetch_remotive(source: dict) -> list[dict]:
    resp = requests.get(source["endpoint"], timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return []
    return resp.json().get("jobs", [])


def fetch_remoteok(source: dict) -> list[dict]:
    resp = requests.get(
        source["endpoint"],
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "job-finder-app-sweep"},
    )
    if resp.status_code != 200:
        return []
    data = resp.json()
    if not isinstance(data, list):
        return []
    # index 0 is a metadata/legal-notice record, not a job — per job-sources-config.md
    return data[1:]


def fetch_arbeitnow(source: dict) -> list[dict]:
    resp = requests.get(source["endpoint"], timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return []
    return resp.json().get("data", [])


_FETCHERS = {
    "remotive": fetch_remotive,
    "remoteok": fetch_remoteok,
    "arbeitnow": fetch_arbeitnow,
}


def fetch_feed_source(source: dict) -> list[dict]:
    fetcher = _FETCHERS.get(source["id"])
    if fetcher is None:
        raise NotImplementedError(f"No FeedAdapter fetcher registered for '{source['id']}'")
    try:
        return fetcher(source)
    except requests.RequestException:
        return []
