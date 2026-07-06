# BUILD-PLAN.md — Job Finder App

Companion to `CLAUDE.md` (the always-true context), `job-sources-config.md` (source catalog), and `ats-company-seed-list.md` (92 verified company tokens). This is the execution order.

**How to use this:** hand Claude Code one phase at a time, alongside CLAUDE.md. Every phase ends with a runnable, checkable deliverable — do not start a phase until the previous one's "Done when" checklist passes. If any instruction here conflicts with CLAUDE.md, CLAUDE.md wins.

---

## Phase 0 — Repo + accounts scaffold (half a day)

Setup that everything else depends on. No app code yet.

**Tasks**
1. Create the GitHub repo (public — unlimited free Actions minutes; the repo contains no secrets).
2. Create the Supabase project (free tier). Note the project URL + anon key + service key.
3. Sign up: Resend (or Brevo) free account → API key.
4. Repo skeleton per CLAUDE.md §11: `/frontend`, `/engine` (with `/adapters`, `/normalize`, `/dedupe`, `/notify`), `/db`, `/.github/workflows`. Copy in `CLAUDE.md`, `job-sources-config.md`, `ats-company-seed-list.md`.
5. Derive `engine/sources.config.json` from job-sources-config.md's machine-readable block, and `engine/seeds/companies.json` from the seed list's combined JSON.
6. Add GitHub Actions secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `RESEND_API_KEY`. (CallMeBot secrets come in Phase 5.)

**Done when:** repo exists with skeleton + both config files; Supabase project reachable; secrets set.

---

## Phase 1 — Database + sweep engine core (the heart) (2–4 days)

Get jobs flowing from sources into the database. No UI yet — verify via SQL.

**Tasks**
1. **Schema + RLS** (`/db`): create `profiles`, `search_criteria`, `jobs`, `user_jobs` exactly per CLAUDE.md §5, with RLS policies (own-rows only; `jobs` shared read). Write as SQL migration files, applied via Supabase SQL editor or CLI.
2. **Engine skeleton** (`/engine`, Python): config loader reads `sources.config.json` + `seeds/companies.json`; canonical Job dataclass per CLAUDE.md §6.
3. **First two adapters:** `ATSJsonAdapter` (Greenhouse first — cleanest, powers 40 of the 92 seed companies; then generalize field mapping to Lever + Ashby) and a `FeedAdapter` for Remotive + RemoteOK (remember: skip RemoteOK's index-0 metadata element) + Arbeitnow.
4. **Normalizer + dedupe:** canonical key, tracking-param stripping, prefer-direct-URL, `(source_id, external_id)` seen-set, `first_seen`/`last_seen`, expiry after 14 days unseen — per job-sources-config.md §Dedupe.
5. **Writer:** upsert normalized jobs into Supabase `jobs` via service key.
6. **Runner:** `python -m engine.sweep` runs end-to-end locally.

**Done when:** one local run pulls from Greenhouse/Lever/Ashby seeds + 3 feeds, and `select count(*) from jobs` shows a deduped pool (expect several thousand rows). Running it twice does not duplicate rows.

## Phase 2 — Matching + schedule (1–2 days)

Turn the global pool into per-user matches, on a timer.

**Tasks**
1. **Matcher:** for each user's `search_criteria`, filter new jobs (title/keyword match against `job_titles[]`, region/remote filters, salary floor where salary data exists — most postings lack it; treat missing salary as "unknown", not "fail"). Insert hits into `user_jobs` with status `new`.
2. Seed one test user + criteria (e.g. `["product designer","brand designer","graphic designer","ui/ux designer","visual designer"]`) directly in the DB and verify matches land.
3. **GitHub Actions workflow** (`sweep.yml`): cron every 3 hours, runs the sweep + matcher. Add a `workflow_dispatch` trigger for manual runs.
4. Keep raw payloads trimmed before storage (free-tier 500 MB — store description text, drop the rest of `raw` for large sources).

**Done when:** the Action runs green on schedule; new matching jobs appear in `user_jobs` for the test user without manual intervention.

## Phase 3 — Frontend: auth + criteria + feed (3–5 days)

The app people actually see. Untitled UI, light + dark.

**Tasks**
1. Vite + React + TS + Tailwind scaffold in `/frontend`; configure **Untitled UI semantic tokens** as CSS variables from day one (CLAUDE.md §2.5 — no hardcoded colors anywhere). Theme toggle = token swap.
2. Supabase Auth: email sign-up/sign-in; on first sign-up, create the `profiles` row.
3. **Criteria screen** (this is onboarding — it's the only setup): job titles (tag input), regions, remote preference, salary floor + currency, source toggles. Editable anytime.
4. **Feed:** list of `user_jobs` joined to `jobs` — title, company, location, remote badge, salary when present, posted date, source badge. Status actions: **Save / Applied / Skip**. "Apply" opens `apply_url` in a new tab. Filters: status tabs (New / Saved / Applied), text search.
5. **Settings:** notification toggles (`notify_email`; WhatsApp toggle rendered only for `role='admin'` — wired in Phase 5), theme, sign out.
6. Deploy to Cloudflare Pages or Vercel free.

**Done when:** you can sign up on the deployed URL, set criteria, and after the next scheduled sweep see real matching jobs in the feed in both themes; marking Applied persists across reload; RLS verified (a second account sees only its own matches).

## Phase 4 — Email notifications (1 day)

1. In the engine's notify step: after matching, for each user with `notify_email = true` and unnotified `user_jobs`, send one **digest email** per sweep run (not one per job) via Resend — job titles, companies, links into the app feed. Set `notified_at`.
2. Respect free limits: batch per user per run; 100/day Resend cap is ample at this scale but assert on it anyway.
3. An unsubscribe path: link to settings; honor the toggle.

**Done when:** test user receives a digest listing exactly the new matches from the latest sweep, once, with working links.

## Phase 5 — Admin WhatsApp (half a day)

1. Chineme signs up normally; flip his `profiles.role` to `admin` via SQL (one-time manual step).
2. He does the one-time CallMeBot authorization from his own phone; add `CALLMEBOT_PHONE` + `CALLMEBOT_APIKEY` as Actions secrets.
3. Engine notify step: if the admin has `notify_whatsapp = true` and new matches, send a compact WhatsApp summary (count + top titles + app link) via the CallMeBot URL call. Non-admins: the code path simply never runs (guard on role, per CLAUDE.md §7).
4. The WhatsApp toggle in settings now works for the admin account.

**Done when:** a sweep with new admin matches produces a WhatsApp message on Chineme's phone; toggling it off stops them; no non-admin path can trigger it.

## Phase 6 — Widen the sources (ongoing, start ~1 week in)

Per the tiers in job-sources-config.md:

1. **Rest of Tier 1:** Workable, SmartRecruiters, Recruitee adapters (same `ats_json` pattern, different field maps); Personio (`XmlAdapter`, **follow redirects** — seed-list note); Himalayas (paginate, 20/req), Jobicy, We Work Remotely **design RSS**, Working Nomads, Get on Board (verify base host); **MyJobMag RSS** — first real Nigeria coverage; HN Who-is-Hiring via Algolia with **regex parsing** (CLAUDE.md §6 — no LLM).
2. **Tier 2 (free keys):** register + add as Actions secrets one by one — **JSearch `country=ng` first** (biggest Nigeria win: reaches LinkedIn/Indeed postings via Google's index), then Adzuna, Jooble, Careerjet, Torre via the `AggregatorAdapter`.
3. **Grow the seed list** per ats-company-seed-list.md §growth rules: bias to agencies, design-as-a-service, DTC, smaller startups; search titles for graphic/brand/visual/creative, not just "design"; manually resolve the African fintechs that 404'd (Flutterwave, Paystack, Kuda, etc.) from their careers pages.
4. **Tier 3 (scrape)** only once everything above is stable: Jobberman (gentle, low frequency), Coroflot, Authentic Jobs.

**Done when (initial pass):** all Tier-1 sources live; JSearch-ng live; seed list >120 companies.

## Phase 7 — Hardening (ongoing)

- Per-source error isolation: one failing source must never kill the sweep (wrap each adapter; log failures to a `sweep_runs` table with per-source status).
- Simple admin view or SQL dashboard: last run time, jobs added per source, failures.
- DB size watch (500 MB): trim descriptions to a max length, drop `raw` after normalization, rely on 14-day expiry.
- Keep Supabase awake (the cron already does).
- Source drift: when a source errors repeatedly, disable via `enabled: false` in config — no code change.

---

## Sequencing summary

| Phase | Duration | Deliverable |
|---|---|---|
| 0 | 0.5 day | Repo + accounts + configs in place |
| 1 | 2–4 days | Jobs flowing into DB from ~10 sources, deduped |
| 2 | 1–2 days | Per-user matching on a 3-hour cron |
| 3 | 3–5 days | Deployed app: auth, criteria, feed, both themes |
| 4 | 1 day | Email digests |
| 5 | 0.5 day | Admin WhatsApp |
| 6 | ongoing | All Tier-1 + JSearch-ng + growing seeds |
| 7 | ongoing | Reliability + monitoring |

Realistic calendar time to a usable product (through Phase 5): **~2 weeks of part-time work**. Everything after that is widening and hardening, not blocking.
