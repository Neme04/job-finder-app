# CLAUDE.md — Job Finder App (working title)

This file guides Claude Code (and any developer) building this project. Read it before writing code. It defines what we're building, the hard rules, the architecture, and how to extend the system. The phased build plan is a separate document; this is the always-true context.

---

## 1. What this is

A **multi-user web app** that automatically finds job postings from many public sources, filters them to each user's search criteria, and shows them in a feed to review and **apply to manually**. Users sign up, set their target job titles and filters, and get notified when new matching jobs drop.

- **Multi-user** from day one: each user has their own isolated search criteria and job feed.
- **One admin account** (Chineme's) gets WhatsApp alerts; everyone else uses email.
- **Not design-only.** Job titles/keywords are user-defined.
- **No AI generation, no auto-apply.** The app finds and surfaces jobs — nothing more.

---

## 2. Hard constraints (do not violate)

1. **$0 cost. No paid services, ever.** With the LLM removed, there are now **zero metered dependencies**. Approved free services are in §4 — do not add anything that bills.
2. **No auto-apply.** The app surfaces jobs; the user clicks "apply" on the source's own site. Auto-submitting to login-walled ATSs risks bans and ToS violations — out of scope.
3. **No AI generation.** The app does **not** write CVs or cover letters, and does not run any LLM. Dropped by design.
4. **Extensible source layer.** Adding a new job source should normally be a **config entry, not new code** (§6). Primary design goal.
5. **Light + dark mode via Untitled UI semantic tokens.** No hardcoded colors; theme switches by token swap.

---

## 3. User flow

1. **Sign up** with email.
2. **Set search criteria:** job titles/keywords, regions, remote preference, salary floor, and which sources to sweep. Editable anytime. **This is the only setup — there is no lengthy profile to fill and nothing to upload.**
3. A **scheduled sweep** runs across the user's enabled sources → dedupes → filters to criteria → stores new matches.
4. **The feed shows matching jobs.** The user marks status (saved / applied / skipped) and applies manually via the source apply URL.
5. **Notifications** fire on new matches: **email** (all users, if enabled), **WhatsApp** (admin only, if enabled).

---

## 4. Tech stack (all free tier)

| Layer | Choice | Why / notes |
|---|---|---|
| **Frontend** | React + Vite + TypeScript + Tailwind CSS, styled with **Untitled UI** | Semantic light/dark tokens + React components. Host free on **Cloudflare Pages** or **Vercel**. |
| **Backend-as-a-service** | **Supabase** (free tier) | Postgres DB + Auth (email) + Row-Level Security for per-user isolation. (Storage not needed — no uploads.) |
| **Sweep + notify engine** | **Python** on **GitHub Actions cron** (free) | Runs on a schedule: runs adapters, dedupes, filters to each user's criteria, writes new jobs to Supabase, sends notifications. Standalone job — language choice is isolated (can be TS). Python favored for the eventual scrape-tier sources. |
| **Email** | **Resend** free (3,000/mo, 100/day) or **Brevo** (300/day) | More than enough for job alerts. Gmail SMTP is a zero-setup fallback. |
| **WhatsApp (admin only)** | **CallMeBot** free API | Personal-use only; messages **only the admin's own authorized number**. |

**No LLM.** Removed entirely — with no generation, nothing is metered.

**Approved free services — do not add paid ones:** Supabase, Cloudflare Pages/Vercel, GitHub Actions, Resend/Brevo, CallMeBot.

**Free-tier caveats to design around:**
- Supabase free projects **pause after ~1 week of inactivity** — the scheduled sweep keeps the DB active. Free DB ~500 MB; trim raw payloads.
- GitHub Actions free minutes: 2,000/mo private, **unlimited public**. A sweep every 2–4 hours stays well within free limits.

---

## 5. Data model (slim)

Core tables, with Row-Level Security so each user sees only their own rows:

- **profiles** — `user_id` (FK auth.users), `role` (`user` | `admin`), `full_name` (optional), `notify_email` (bool), `notify_whatsapp` (bool).
- **search_criteria** — `profile_id`, `job_titles[]`, `regions[]`, `remote_pref`, `salary_floor`, `currency`, `sources_enabled[]`.
- **jobs** — the **shared, deduped global pool**: `canonical_key`, `source_id`, `external_id`, `title`, `company`, `location`, `remote`, `description`, `apply_url`, `salary_min`, `salary_max`, `currency`, `posted_at`, `first_seen`, `last_seen`.
- **user_jobs** — the per-user layer: `profile_id`, `job_id`, `status` (new / saved / applied / skipped), `notified_at`.

**RLS:** users read/write only their own `profiles`, `search_criteria`, and `user_jobs`. The `jobs` pool is shared read. WhatsApp fields/actions gated on `role = 'admin'`.

**Removed vs. the earlier draft:** `work_history`, `projects`, `skills`, `screening_answers`, `documents`, `voice_sample`. These existed only to power CV/cover-letter generation and auto-apply — both dropped, so they carry no purpose now.

---

## 6. Source layer — the extensibility centerpiece

**Goal:** adding a new job source is normally a JSON entry, not new code. The full catalog (endpoints, access methods, tiers) lives in **`job-sources-config.md`** — the canonical reference. Derive a machine-readable `sources.config.json` from it.

### Registry entry (one per source)
```json
{
  "id": "greenhouse",
  "name": "Greenhouse",
  "type": "ats_json",
  "auth": "none",
  "endpoint_template": "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true",
  "params": [],
  "needs": "company_tokens",
  "region": "global",
  "roles": "all",
  "tier": 1,
  "enabled": true
}
```

### Adapter model (few generic adapters, many config entries)
- One generic adapter **per `type`**: `ATSJsonAdapter`, `RssAdapter`, `AggregatorAdapter`, `ScrapeAdapter`.
- Each adapter takes a registry entry + the user's criteria, fetches, returns **raw records**.
- A **normalizer** (per type, with optional per-source field mapping) maps raw records → the **canonical Job schema**.
- **Adding a source of an existing type = add a JSON entry** (+ optional field mapping). **A new type = add one adapter class.** That's the whole extension story.

### Canonical Job schema (every adapter normalizes to this)
```
canonical_key, source_id, external_id, title, company, location, remote,
description, apply_url, salary_min, salary_max, currency, posted_at, raw
```

### Source tiers (full list in job-sources-config.md)
- **Tier 1 — frictionless (no key, no login):** Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Personio (ATS, per-company — needs a company seed list); Remotive, RemoteOK, Himalayas, Arbeitnow, Jobicy, We Work Remotely (RSS), Working Nomads, Get on Board; Hacker News "Who is Hiring" (Algolia); MyJobMag (RSS, Nigeria/Africa).
- **Tier 2 — free API key:** JSearch (`country=ng` — key source for Nigeria via Google-for-Jobs), Adzuna, Jooble, Careerjet, Torre.
- **Tier 3 — scrape-only (add last):** Jobberman, Coroflot, Authentic Jobs.

**ATS APIs are per-company** — one call returns one company's board. The app needs a **seed list of company tokens/slugs per ATS** that grows over time. Building it is the first Phase-1 task.

**Hacker News parsing:** the "Who is Hiring" comments are unstructured. Parse them with **deterministic regex** (company / role / remote / apply link), not an LLM. This source is optional.

### Dedupe (runs across all normalized jobs — see job-sources-config.md §Dedupe)
Canonical key = `normalize(company) :: normalize(title) :: normalize(location)`; strip tracking params from apply URLs; prefer the **direct source apply URL** over aggregator redirects; fuzzy-match near-dupes; persist `(source_id, external_id)` across runs; expire jobs that vanish from source after N days.

---

## 7. Notifications

- **Email — all users.** Sent via Resend (or Brevo) from the sweep engine when a user has new matches and `notify_email` is on. Free tier covers it.
- **WhatsApp — admin only.** Sent via CallMeBot to the **admin's own authorized number**. The admin's CallMeBot API key + phone are **server-side secrets**, not collected from users. The WhatsApp toggle only appears and only works for `role = 'admin'`. Keeps us within CallMeBot's personal-use terms and at $0.
- **Per-user toggles** on the profile (`notify_email`, `notify_whatsapp`). A user can enable both; WhatsApp is inert for non-admins.
- **The sweep triggers notifications** — "alert me when a job drops" requires the 24/7 cron to detect the drop, independent of the UI. Notifications are not sent from the frontend.

---

## 8. Security & privacy

- All user data isolated by Supabase **Row-Level Security**. Verify RLS on every table before shipping.
- **All secrets server-side:** Resend key, CallMeBot key/phone, Supabase service key. Never in the frontend bundle or the repo.
- The frontend only uses the Supabase anon key with RLS enforced.
- Small surface: no CVs/PII uploaded, no third-party LLM receiving user data.

---

## 9. Coding conventions

- **TypeScript strict** on the frontend and any TS code.
- **Untitled UI semantic tokens only** — never hardcode color; theming works by token swap. Follow the design system's type scale, spacing, radii, shadows.
- **Source adapters are isolated and pure** — fetch + normalize, no side effects; persistence happens in one place.
- **One canonical Job schema** — everything normalizes to it before dedupe/storage.
- Trim raw source payloads before storing (free-tier DB size).
- Prefer config over code for anything source-related.

---

## 10. Explicitly out of scope

- **AI generation of CVs / cover letters** (dropped by design). No LLM in the system.
- **Elaborate user profiles / "profile brain"** — no feature needs it now.
- **Auto-apply / login-walled scraping** (LinkedIn/Workday credential automation) — ban + ToS risk. We reach those markets **indirectly** via JSearch's Google-for-Jobs index.
- Any paid API or hosting tier; WhatsApp for non-admin users.

---

## 11. Suggested repo layout
```
/frontend        React + Vite + TS + Tailwind (Untitled UI)
/engine          Python sweep + notify (runs on GitHub Actions cron)
  /adapters      ats_json, rss, aggregator, scrape
  /normalize     raw -> canonical Job
  /dedupe
  /notify        email (Resend) + whatsapp (CallMeBot, admin)
  sources.config.json   (derived from job-sources-config.md)
/db              Supabase schema + RLS policies + migrations
/.github/workflows   sweep.yml (cron)
CLAUDE.md
job-sources-config.md
```
(No `/functions` — no AI endpoints needed.)

---

## 12. Next

The **phased build plan** is the next document. In short: **Phase 1** stands up auth + search criteria + the ATS company seed list + a handful of Tier-1 sources + the feed, all at $0. Phase 1 cannot pull ATS jobs until the **company seed list** exists — build that first.
