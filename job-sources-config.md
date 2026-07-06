# Job Sources Config — Sweepable Boards (Free, No Login)

This is the buildable source list for the app: every board that is **free** and **not behind a login wall**, with the exact access method, endpoint template, what it returns, and how to sweep it. Endpoints below were verified current as of July 2026. Hand this to Claude Code as the source layer spec.

## How to read the tiers

- **Tier 1 — Frictionless:** open API or RSS. No key, no signup, no login. Build these first.
- **Tier 2 — Free key:** free to use but you register once for an API key. Adds reach into Nigeria/Africa/LATAM/UK.
- **Tier 3 — Scrape-only:** no API or feed; public HTML you parse yourself. Highest maintenance, breaks most often. Add last.

**The single most important architectural note:** the seven ATS APIs are not "one board each." Each is one *pattern* that unlocks the public careers page of any company using that ATS — but you query **per company**, not globally. One Greenhouse call returns one company's jobs. So the app needs a **seed list of company board tokens/slugs per ATS** that you curate and grow over time. That seed list is where your real coverage comes from, not the remote feeds.

---

## Tier 1 — Frictionless (no key, no login) — the MVP

### ATS APIs (query per company; need a company seed list)

| Source | Endpoint template | Auth | Returns | Notes |
|---|---|---|---|---|
| **Greenhouse** | `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` | None | Title, location, department, full description, apply URL, updated date | Cleanest ATS feed; best place to start. `?content=true` includes descriptions. |
| **Lever** | `https://api.lever.co/v0/postings/{company}?mode=json` | None | Title, categories (team/location/commitment), description, hosted + apply URLs, optional salary | Very clean JSON. |
| **Ashby** | `https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true` | None | Title, location, department, description, apply URL, comp (when set) | Lots of well-funded startups; strong for design/product roles. |
| **Workable** | `https://apply.workable.com/api/v1/widget/accounts/{subdomain}?details=true` | None | Account name + published jobs: title, location, department, description, apply URL | Per-account only; no cross-company aggregation. No filtering — pull all, filter your side. |
| **SmartRecruiters** | `https://api.smartrecruiters.com/v1/companies/{company}/postings` | None | Title, location, department, function, apply URL; fetch posting detail for full description | Public postings endpoint, no auth. |
| **Recruitee** | `https://{company}.recruitee.com/api/offers/` | None | Title, location, department, description, careers + apply URLs | Simple per-subdomain offers feed. |
| **Personio** | `https://{company}.jobs.personio.com/xml` | None | XML: title, location, department, description, employment type | XML not JSON. Some tenants use `.jobs.personio.de` — confirm per company. |

**Getting board tokens:** the `{token}`/`{company}`/`{subdomain}` is the company's slug on that ATS (visible in their careers page URL). Seed the app with a starter list of companies you care about (remote-first, African, design-heavy, etc.) and let it grow. A company only appears if it uses that specific ATS.

### Remote job feeds (global, one call returns many companies)

| Source | Endpoint | Auth | Returns | Notes |
|---|---|---|---|---|
| **Remotive** | `https://remotive.com/api/remote-jobs?category={cat}&search={q}&limit={n}` | None | Title, company, salary, tags, category, description, apply URL | ~70K curated remote jobs; supports category + text filter. |
| **RemoteOK** | `https://remoteok.com/api` | None | Title, company, salary, tags, location, apply URL | **First array element is metadata/legal — skip index 0.** Attribution requested. |
| **Himalayas** | Browse: `https://himalayas.app/jobs/api?limit=20&offset=0` · Search: `https://himalayas.app/jobs/api/search` | None | Title, company, salary, seniority, timezone, description, apply URL | Max **20 jobs/request** (paginate with offset). Attribution required; don't resubmit their jobs to third parties. |
| **Arbeitnow** | `https://www.arbeitnow.com/api/job-board-api` | None | Title, company, location, tags, description, apply URL | Europe-leaning, lots of tech; paginated. |
| **Jobicy** | `https://jobicy.com/api/v2/remote-jobs?count=50&geo={geo}&industry={ind}&tag={tag}` | None | Title, company, geo, industry, type, description, apply URL | Filter by geo/industry/tag. |
| **We Work Remotely** | RSS: `https://weworkremotely.com/remote-jobs.rss` · Design: `https://weworkremotely.com/categories/remote-design-jobs.rss` | None (RSS) | Title, company, region, description, apply URL | RSS only, no JSON API. Category feeds are useful — the design one is directly relevant for Chineme. |
| **Working Nomads** | `https://www.workingnomads.com/api/exposed_jobs/` | None | Title, company, category, tags, description, apply URL | Confirm endpoint path at build time — it has shifted before. |

### Community + regional (Tier 1)

| Source | Access | Auth | Returns | Notes |
|---|---|---|---|---|
| **Get on Board** | Public API — base per `api-doc.getonbrd.com`, e.g. `/v0/categories/{category}/jobs`, `/v0/search/jobs?query={q}` | None (public facet) | Categories, companies, jobs, remote modality, tags; free-text job search | LATAM + remote tech focus. Public facet needs no key; confirm base host in the API reference. |
| **Hacker News "Who is Hiring?"** | 1) Find threads: `https://hn.algolia.com/api/v1/search?query=Ask HN: Who is hiring?&tags=story,author_whoishiring` → 2) Pull whole thread: `https://hn.algolia.com/api/v1/items/{threadId}` | None | Monthly thread → hundreds of founder-posted roles as **plain-text comments** | ~10K req/hr (effectively unmetered). Comments are unstructured → parse with regex or an LLM to extract company/role/remote/apply. Startup-heavy, often remote. |
| **MyJobMag** | RSS index: `https://www.myjobmag.com/feeds/` | None (RSS) | Title, company, location, description, apply/detail URL | **Nigeria, Ghana, Kenya, South Africa** feeds. The most sweepable African source — real RSS, no scraping. High value for Chineme's local + pan-African search. |

---

## Tier 2 — Free but need a free API key

Register once, drop the key in the app's env. These are your reach into markets the Tier-1 feeds miss — especially **Nigeria and Africa**.

| Source | Endpoint | Key | Returns | Region value |
|---|---|---|---|---|
| **JSearch** (OpenWeb Ninja) | `https://jsearch.p.rapidapi.com/search?query={q}&country={cc}` (header `x-rapidapi-key`) or direct portal (`x-api-key`) | Free tier, no card | Live listings + apply links aggregated from **Google for Jobs** (LinkedIn, Indeed, Glassdoor, ZipRecruiter, etc.) | **Supports `country=ng` (Nigeria), plus za, gh, ke** and many more. Highest-value keyed source for Chineme — indirectly reaches login-walled boards via Google's index. |
| **Adzuna** | `https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id={id}&app_key={key}&what={q}&where={loc}` | Free tier (app_id + app_key) | Title, company, location, salary, description, apply URL | ~19 countries incl. **za** (South Africa), gb, us, in. No direct Nigeria, but ZA + remote helps. Generous free limits. |
| **Jooble** | POST `https://jooble.org/api/{key}` body `{"keywords": "...", "location": "..."}` | Free key | Title, company, location, snippet, apply URL | Global incl. Nigeria. Simple POST. |
| **Careerjet** | `http://public.api.careerjet.net/search?keywords={q}&location={loc}&affid={affiliateId}` | Free affiliate ID | Title, company, locations, description snippet, apply URL | Very broad country coverage incl. Nigeria. |
| **Torre** | POST `https://search.torre.co/opportunities/_search` | None/light | Title, org, remote flag, compensation, skills, apply URL | LATAM-heavy but global remote. Public search endpoint. |

*(Torre is close to keyless — grouped here since it's a POST search API rather than a simple feed.)*

---

## Tier 3 — Scrape-only (no API/feed; add last)

Public HTML, parsed with BeautifulSoup/Playwright. Layouts change, some have anti-bot — treat as best-effort, wrap in retries, expect breakage.

| Source | Target | Focus | Risk |
|---|---|---|---|
| **Jobberman** | `https://www.jobberman.com/jobs` | Nigeria/Africa, all industries | SEEK-owned; anti-bot likely. Scrape gently, low frequency. |
| **Coroflot** | `https://www.coroflot.com/design-jobs` | Design-native (product/UI/graphic) | Straightforward scrape; directly relevant for Chineme. |
| **Authentic Jobs** | `https://authenticjobs.com` (RSS where available, else scrape) | Design + dev | Historic API deprecated; RSS/scrape only. |

---

## Machine-readable config (drop into the app)

```json
{
  "ats_sources": [
    { "id": "greenhouse", "type": "ats", "auth": "none", "endpoint": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true", "needs": "company_tokens", "region": "global", "priority": 1 },
    { "id": "lever", "type": "ats", "auth": "none", "endpoint": "https://api.lever.co/v0/postings/{company}?mode=json", "needs": "company_slugs", "region": "global", "priority": 1 },
    { "id": "ashby", "type": "ats", "auth": "none", "endpoint": "https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true", "needs": "board_names", "region": "global", "priority": 1 },
    { "id": "workable", "type": "ats", "auth": "none", "endpoint": "https://apply.workable.com/api/v1/widget/accounts/{subdomain}?details=true", "needs": "subdomains", "region": "global", "priority": 2 },
    { "id": "smartrecruiters", "type": "ats", "auth": "none", "endpoint": "https://api.smartrecruiters.com/v1/companies/{company}/postings", "needs": "company_ids", "region": "global", "priority": 2 },
    { "id": "recruitee", "type": "ats", "auth": "none", "endpoint": "https://{company}.recruitee.com/api/offers/", "needs": "subdomains", "region": "global", "priority": 2 },
    { "id": "personio", "type": "ats", "auth": "none", "format": "xml", "endpoint": "https://{company}.jobs.personio.com/xml", "needs": "subdomains", "region": "EU-leaning", "priority": 2 }
  ],
  "feed_sources": [
    { "id": "remotive", "type": "feed", "auth": "none", "endpoint": "https://remotive.com/api/remote-jobs", "params": ["category", "search", "limit"], "region": "remote-global", "priority": 1 },
    { "id": "remoteok", "type": "feed", "auth": "none", "endpoint": "https://remoteok.com/api", "note": "skip index 0 (metadata)", "region": "remote-global", "priority": 1 },
    { "id": "himalayas", "type": "feed", "auth": "none", "endpoint": "https://himalayas.app/jobs/api", "search_endpoint": "https://himalayas.app/jobs/api/search", "max_per_request": 20, "region": "remote-global", "priority": 2 },
    { "id": "arbeitnow", "type": "feed", "auth": "none", "endpoint": "https://www.arbeitnow.com/api/job-board-api", "region": "EU-remote", "priority": 1 },
    { "id": "jobicy", "type": "feed", "auth": "none", "endpoint": "https://jobicy.com/api/v2/remote-jobs", "params": ["count", "geo", "industry", "tag"], "region": "remote-global", "priority": 2 },
    { "id": "weworkremotely", "type": "rss", "auth": "none", "endpoint": "https://weworkremotely.com/remote-jobs.rss", "design_feed": "https://weworkremotely.com/categories/remote-design-jobs.rss", "region": "remote-global", "priority": 2 },
    { "id": "workingnomads", "type": "feed", "auth": "none", "endpoint": "https://www.workingnomads.com/api/exposed_jobs/", "verify_endpoint": true, "region": "remote-global", "priority": 3 },
    { "id": "getonboard", "type": "feed", "auth": "none", "endpoint_ref": "api-doc.getonbrd.com (/v0/search/jobs, /v0/categories/{cat}/jobs)", "verify_host": true, "region": "LATAM-remote", "priority": 3 },
    { "id": "myjobmag", "type": "rss", "auth": "none", "endpoint": "https://www.myjobmag.com/feeds/", "region": "NG/GH/KE/ZA", "priority": 2 }
  ],
  "hn_source": {
    "id": "hn_whoishiring", "type": "community", "auth": "none",
    "thread_search": "https://hn.algolia.com/api/v1/search?query=Ask HN: Who is hiring?&tags=story,author_whoishiring",
    "thread_fetch": "https://hn.algolia.com/api/v1/items/{threadId}",
    "parse": "regex_or_llm", "region": "startup-global", "priority": 2
  },
  "keyed_sources": [
    { "id": "jsearch", "type": "aggregator", "auth": "api_key", "endpoint": "https://jsearch.p.rapidapi.com/search", "params": ["query", "country", "page"], "covers": ["ng", "za", "gh", "ke", "global"], "priority": 1, "note": "reaches Google-for-Jobs incl. LinkedIn/Indeed" },
    { "id": "adzuna", "type": "aggregator", "auth": "app_id_key", "endpoint": "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}", "params": ["what", "where", "app_id", "app_key"], "covers": ["za", "gb", "us", "in", "+15"], "priority": 2 },
    { "id": "jooble", "type": "aggregator", "auth": "api_key", "method": "POST", "endpoint": "https://jooble.org/api/{key}", "body": ["keywords", "location"], "covers": ["global", "ng"], "priority": 2 },
    { "id": "careerjet", "type": "aggregator", "auth": "affiliate_id", "endpoint": "http://public.api.careerjet.net/search", "params": ["keywords", "location", "affid"], "covers": ["global", "ng"], "priority": 3 },
    { "id": "torre", "type": "aggregator", "auth": "none", "method": "POST", "endpoint": "https://search.torre.co/opportunities/_search", "covers": ["LATAM", "remote-global"], "priority": 3 }
  ],
  "scrape_sources": [
    { "id": "jobberman", "type": "scrape", "target": "https://www.jobberman.com/jobs", "region": "NG/Africa", "risk": "anti-bot", "priority": 4 },
    { "id": "coroflot", "type": "scrape", "target": "https://www.coroflot.com/design-jobs", "region": "global", "focus": "design", "priority": 4 },
    { "id": "authenticjobs", "type": "scrape", "target": "https://authenticjobs.com", "region": "global", "focus": "design/dev", "priority": 4 }
  ]
}
```

---

## Dedupe strategy (essential — the same job appears on many sources)

Aggregators like JSearch and Adzuna pull from Google for Jobs, which indexes the very ATS pages you're already sweeping directly. So the same role will show up two or three times. Handle it in this order:

1. **Canonical key per posting:** `normalize(company) + "::" + normalize(title) + "::" + normalize(location)`. Normalize = lowercase, strip punctuation, collapse whitespace, drop seniority filler words inconsistently applied.
2. **Strip tracking params from apply URLs** before comparing (`utm_*`, `gh_src`, `?ref=`, etc.). Aggregator links wrap the real URL in redirects — extract the destination where possible.
3. **Prefer the direct source.** When a duplicate is found, keep the record with the **direct ATS/company apply URL** over the aggregator's redirect link. Direct = better apply experience and cleaner data.
4. **Fuzzy match for near-dupes:** token-set ratio on `title + company` with a threshold (~90+) to catch "Senior Product Designer" vs "Sr. Product Designer, Product" from two feeds.
5. **Cross-run seen-set:** persist `(source_id, external_id)` so re-running the sweep doesn't re-insert the same posting. Store `first_seen` and `last_seen` timestamps.
6. **Expiry:** if a posting stops appearing in its source for N days (e.g. 14), mark it closed. Prevents a stale, dead-link feed.

---

## Recommended build order

**Phase 1 — prove the loop, zero keys.** Greenhouse + Lever + Ashby (seed ~30–50 companies you care about) + Remotive + RemoteOK + Arbeitnow + HN Who-is-Hiring. This alone gives global tech/remote/startup coverage including design roles, with no signups.

**Phase 2 — widen, still zero keys.** Add Workable, SmartRecruiters, Recruitee, Personio, Himalayas, Jobicy, We Work Remotely (incl. the design RSS), Working Nomads, Get on Board, and **MyJobMag RSS** (your first real Nigeria/Africa coverage).

**Phase 3 — reach the walled markets via keys.** Add **JSearch with `country=ng`** (the big one for Chineme — pulls Nigerian roles that live on LinkedIn/Indeed via Google's index), Adzuna (za), Jooble, Careerjet, Torre.

**Phase 4 — optional, higher maintenance.** Scrape Jobberman, Coroflot, Authentic Jobs. Only worth it once everything above is stable.

**For Chineme's design search specifically**, the highest-signal sources are: Ashby + Greenhouse + Lever (startup design roles), We Work Remotely's design RSS, Coroflot, and JSearch `country=ng` — plus MyJobMag for local Lagos/Nigeria postings.

---

## Two honest caveats

- **ATS coverage depends entirely on your seed list.** No seed company on Greenhouse = no Greenhouse jobs. Budget time for building and growing that list; consider a public ATS-company directory to bootstrap it.
- **Verify three items at build time:** the Get on Board API base host, the Working Nomads endpoint path, and whether each Personio tenant uses `.com` or `.de`. These are the only three where the exact string may have drifted.
