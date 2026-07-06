"""Generic ATS JSON adapter — one class, many companies, per source registry entry.

Fetch is pure: given a registry entry + a company token, return raw records.
No normalization or persistence here (that happens in engine/normalize and the writer).
"""

import requests

REQUEST_TIMEOUT = 15

# maps ats source id -> function(endpoint_template, token) -> list[raw record dict]
_SEED_KEY_BY_SOURCE = {
    "greenhouse": "greenhouse",
    "lever": "lever",
    "ashby": "ashby",
}


def fetch_greenhouse(endpoint_template: str, token: str) -> list[dict]:
    url = endpoint_template.format(token=token)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return []
    data = resp.json()
    jobs = data.get("jobs", [])
    for j in jobs:
        j["_company_token"] = token
    return jobs


def fetch_lever(endpoint_template: str, company: str) -> list[dict]:
    url = endpoint_template.format(company=company)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return []
    data = resp.json()
    if not isinstance(data, list):
        return []
    for j in data:
        j["_company_token"] = company
    return data


def fetch_ashby(endpoint_template: str, board: str) -> list[dict]:
    url = endpoint_template.format(board=board)
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code != 200:
        return []
    data = resp.json()
    jobs = data.get("jobs", [])
    for j in jobs:
        j["_company_token"] = board
    return jobs


_FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
}


def fetch_ats_source(source: dict, seeds: dict) -> list[dict]:
    """Fetch raw records for every seeded company under one ATS source."""
    source_id = source["id"]
    fetcher = _FETCHERS.get(source_id)
    if fetcher is None:
        raise NotImplementedError(f"No ATSJsonAdapter fetcher registered for '{source_id}'")

    seed_key = _SEED_KEY_BY_SOURCE.get(source_id, source_id)
    tokens = seeds.get(seed_key, [])

    raw_records: list[dict] = []
    for token in tokens:
        try:
            raw_records.extend(fetcher(source["endpoint"], token))
        except requests.RequestException:
            continue
    return raw_records
