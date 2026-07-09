"""End-to-end sweep runner: fetch -> normalize -> dedupe -> write.

Run with: python -m engine.sweep
Requires SUPABASE_URL and SUPABASE_SERVICE_KEY in the environment.
"""

from engine.adapters.ats_json import fetch_ats_source
from engine.adapters.feed import fetch_feed_source
from engine.config import (
    enabled_ats_sources,
    enabled_feed_sources,
    load_company_seeds,
    load_sources_config,
)
from engine.dedupe import dedupe_jobs
from engine.matcher import run_matcher
from engine.models import Job
from engine.normalize import normalize_records
from engine.notify import run_email_notify
from engine.writer import expire_stale_jobs, upsert_jobs


def collect_jobs() -> list[Job]:
    config = load_sources_config()
    seeds = load_company_seeds()

    jobs: list[Job] = []

    for source in enabled_ats_sources(config):
        raw = fetch_ats_source(source, seeds)
        normalized = normalize_records(source["id"], raw)
        print(f"[{source['id']}] fetched {len(raw)} raw, normalized {len(normalized)}")
        jobs.extend(normalized)

    for source in enabled_feed_sources(config):
        raw = fetch_feed_source(source)
        normalized = normalize_records(source["id"], raw)
        print(f"[{source['id']}] fetched {len(raw)} raw, normalized {len(normalized)}")
        jobs.extend(normalized)

    return jobs


def main() -> None:
    jobs = collect_jobs()
    print(f"total normalized: {len(jobs)}")

    deduped = dedupe_jobs(jobs)
    print(f"after dedupe: {len(deduped)}")

    written = upsert_jobs(deduped)
    print(f"upserted: {written}")

    expire_stale_jobs()
    print("expired stale jobs older than 14 days")

    matched = run_matcher()
    print(f"matched (criteria hits attempted, duplicates ignored): {matched}")

    notified = run_email_notify()
    print(f"email digests sent: {notified}")


if __name__ == "__main__":
    main()
