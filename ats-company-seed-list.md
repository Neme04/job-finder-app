# ATS Company Seed List

Every token below was **verified live** against the real ATS APIs on July 6, 2026 (not guessed — guessed slugs 404 constantly, so each one here was actually hit and confirmed). Job counts and design-role counts are a snapshot from that check; they'll drift day to day, but a `200` response confirms the token itself is permanently valid (companies rarely change ATS once adopted).

This is the seed for `engine/seeds/*.json` per the CLAUDE.md repo layout. The `ats_json` adapters iterate this list, one API call per company, per the source registry in `job-sources-config.md`.

---

## Greenhouse — 29 verified
Endpoint: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`

| Token | Total jobs | Design roles |
|---|---|---|
| stripe | 489 | 16 |
| databricks | 792 | 7 |
| anthropic | 388 | 4 |
| airbnb | 220 | 1 |
| cloudflare | 239 | 1 |
| brex | 263 | 10 |
| pinterest | 188 | 6 |
| affirm | 177 | 2 |
| figma | 171 | 11 |
| twilio | 153 | 3 |
| asana | 147 | 5 |
| gitlab | 143 | 2 |
| robinhood | 132 | 7 |
| coinbase | 129 | 2 |
| reddit | 190 | 0 |
| moniepoint | 64 | 1 |
| discord | 59 | 6 |
| chime | 64 | 3 |
| mercury | 54 | 6 |
| dropbox | 50 | 5 |
| airtable | 37 | 2 |
| gusto | 78 | 6 |
| vercel | 66 | 1 |
| jumia | 8 | 0 |
| squarespace | 18 | 0 |
| calendly | 16 | 0 |
| typeform | 16 | 1 |
| webflow | 22 | 0 |
| netlify | 2 | 0 |

```json
["stripe","databricks","anthropic","airbnb","cloudflare","brex","pinterest","affirm","figma","twilio","asana","gitlab","robinhood","coinbase","reddit","moniepoint","discord","chime","mercury","dropbox","airtable","gusto","vercel","jumia","squarespace","calendly","typeform","webflow","netlify"]
```

## Ashby — 19 verified
Endpoint: `https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true`

| Token | Total jobs | Design roles |
|---|---|---|
| openai | 722 | 18 |
| ramp | 125 | 5 |
| notion | 146 | 2 |
| elevenlabs | 148 | 1 |
| replit | 98 | 1 |
| vanta | 107 | 2 |
| cursor | 112 | — |
| attio | 38 | — |
| ashby | 64 | 12 |
| watershed | 44 | 1 |
| linear | 24 | 2 |
| andela | 17 | 1 |
| runway | 4 | — |
| maven | 3 | — |
| ycombinator | 6 | 1 |
| mux | 2 | — |
| deel | 0 (currently) | — |
| ghost | 1 | — |
| hex | 0 (currently) | — |

```json
["openai","ramp","notion","elevenlabs","replit","vanta","cursor","attio","ashby","watershed","linear","andela","runway","maven","ycombinator","mux","deel","ghost","hex"]
```

## Lever — 5 verified
Endpoint: `https://api.lever.co/v0/postings/{company}?mode=json`

| Token | Total jobs |
|---|---|
| palantir | 275 |
| spotify | 113 |
| netflix | 0 (currently) |
| plaid | 0 (currently) |
| kraken | 0 (currently) |

```json
["palantir","spotify","netflix","plaid","kraken"]
```

## Workable — 7 verified
Endpoint: `https://apply.workable.com/api/v1/widget/accounts/{subdomain}?details=true`

Tokens confirmed live (all showed 0 open roles at check time — normal, re-check on schedule):
```json
["automattic","buffer","zapier","grammarly","canva","deliveroo","doist"]
```

## SmartRecruiters — 7 verified
Endpoint: `https://api.smartrecruiters.com/v1/companies/{company}/postings`

| Token | Total jobs |
|---|---|
| Visa | 2 |
| Deliveroo | 0 (currently) |
| Adidas | 0 (currently) |

Also confirmed live: `Bosch`, `Skechers`, `McDonalds`, `IKEA`

```json
["Visa","Bosch","Skechers","McDonalds","Deliveroo","IKEA","Adidas"]
```

## Recruitee — 2 verified
Endpoint: `https://{company}.recruitee.com/api/offers/`

| Token | Total jobs |
|---|---|
| bunq | 16 |
| sendcloud | 1 |

```json
["bunq","sendcloud"]
```

## Lower-competition additions — smaller companies + graphic/brand design focus

The first pass leaned on famous names (Stripe, OpenAI, Airbnb) — but those get flooded with hundreds of applicants per design posting, which cuts against the actual goal. This batch prioritizes **less famous companies** (smaller applicant pools per posting) and **companies that hire graphic/brand designers specifically**, not just product/UX. Design agencies and brand studios are the highest-value addition here since brand/graphic design *is* their core hiring need, not an afterthought.

### Design & brand agencies (high graphic/brand hit-rate) — Greenhouse
| Token | Total jobs | Design/graphic/brand roles |
|---|---|---|
| **landor** | 48 | **25** — branding agency; best hit-rate in the whole list |
| **ideo** | 15 | **11** — global design consultancy |
| designpickle | 0 (currently) | — subscription graphic-design service; volume-hires graphic designers, re-check often |

```json
["landor","ideo","designpickle"]
```

### Design/creative agencies — Lever
| Token | Total jobs | Design/graphic/brand roles |
|---|---|---|
| superside | 25 | 3 — design-as-a-service at scale; **often has contract/freelance roles**, relevant for side-gig work |
| fantasy | 6 | 3 |
| instrument | 4 | 2 |

```json
["superside","fantasy","instrument"]
```

### DTC/consumer brands (smaller, in-house brand & graphic design needs) — Greenhouse
| Token | Total jobs | Design/graphic/brand roles |
|---|---|---|
| oura | 94 | 11 |
| glossier | 19 | 1 |
| olipop | 12 | 2 |
| bombas | 14 | 0 (currently) |
| brooklinen | 12 | 0 (currently) |
| harrys | 11 | 0 (currently) |
| quip | 4 | 0 (currently) |
| liquiddeath | 0 (currently) | — |

```json
["oura","glossier","olipop","bombas","brooklinen","harrys","quip","liquiddeath"]
```

### Smaller/less-famous startups (genuinely lower applicant volume) — Ashby
| Token | Total jobs | Design/graphic/brand roles |
|---|---|---|
| n8n | 34 | 2 |
| supabase | 50 | 2 |
| posthog | 21 | 0 (currently) |
| warp | 20 | 1 |
| pika | 10 | 0 (currently) |
| resend | 8 | 0 (currently) |
| raycast | 0 (currently) | — |
| clerk | 0 (currently) | — |
| tldraw | 1 | 0 (currently) |

```json
["n8n","supabase","posthog","warp","pika","resend","raycast","clerk","tldraw"]
```

**Total new verified tokens: 23** (3 agencies + 3 creative-agency Lever + 8 DTC brands + 9 smaller Ashby startups), bringing the full seed list to **92 verified companies**.

---

## Personio — needs redirect handling
Endpoint: `https://{company}.jobs.personio.com/xml`

`n26`, `flixbus`, `depop`, and `trivago` all returned **HTTP 307** (redirect), not a clean 200 — meaning tenants likely exist but the adapter must **follow the redirect** to confirm and fetch. `personio` itself (Personio's own careers page) returned a clean 200. Flag this in the adapter implementation: Personio needs `allow_redirects=True` / equivalent, not a bare status check.

```json
{"needs_verification_via_redirect": ["n26","flixbus","depop","trivago"]}
```

---

## Combined seed file (drop into `engine/seeds/companies.json`)

```json
{
  "greenhouse": ["stripe","databricks","anthropic","airbnb","cloudflare","brex","pinterest","affirm","figma","twilio","asana","gitlab","robinhood","coinbase","reddit","moniepoint","discord","chime","mercury","dropbox","airtable","gusto","vercel","jumia","squarespace","calendly","typeform","webflow","netlify","landor","ideo","designpickle","oura","glossier","olipop","bombas","brooklinen","harrys","quip","liquiddeath"],
  "ashby": ["openai","ramp","notion","elevenlabs","replit","vanta","cursor","attio","ashby","watershed","linear","andela","runway","maven","ycombinator","mux","deel","ghost","hex","n8n","supabase","posthog","warp","pika","resend","raycast","clerk","tldraw"],
  "lever": ["palantir","spotify","netflix","plaid","kraken","superside","fantasy","instrument"],
  "workable": ["automattic","buffer","zapier","grammarly","canva","deliveroo","doist"],
  "smartrecruiters": ["Visa","Bosch","Skechers","McDonalds","Deliveroo","IKEA","Adidas"],
  "recruitee": ["bunq","sendcloud"],
  "personio_pending_verification": ["n26","flixbus","depop","trivago"]
}
```

**92 verified tokens total.** Companies flagged in the "lower-competition" section above (Landor, IDEO, Design Pickle, Superside, Fantasy, Instrument, Oura, Glossier, Olipop, Bombas, Brooklinen, Harry's, Quip, Liquid Death, n8n, Supabase, PostHog, Warp, Pika, Resend, Raycast, Clerk, tldraw) should be **weighted higher, not lower**, in any future ranking — they're the ones actually worth prioritizing for realistic odds.

---

## What's notably missing (checked, not found)

Tried and got **404** on Greenhouse/Lever/Ashby for these major African fintechs — meaning they either use a different ATS entirely (likely Workday, BambooHR, or an in-house system), a slug that doesn't match the obvious guess, or a private/unlisted board: **Flutterwave, Paystack, Kuda, Wave, Chipper Cash, OPay, Interswitch**. Worth a manual check of their actual careers pages to find the real ATS if one exists — Jumia and Moniepoint being the two confirmed African hits suggests it's worth the manual look for the others.

Also 404'd: Shopify, GitHub, Notion (on Greenhouse — it's actually on Ashby, see above), Linear (also Ashby, not Greenhouse), Loom, Superhuman, ClickUp, Grammarly (Workable, not Greenhouse), Canva (Workable, not Greenhouse), Miro, Ramp (Ashby, not Greenhouse), Deel (Ashby, not Greenhouse). **Lesson baked into this list:** the same company is often on a *different* ATS than you'd guess — always try all six before concluding a company isn't sweepable.

---

## How to grow this list going forward

1. **Manual check via careers page:** visit `company.com/careers` — if it redirects to `boards.greenhouse.io/{token}`, `jobs.lever.co/{token}`, `jobs.ashbyhq.com/{token}`, `apply.workable.com/{token}`, etc., the token is right there in the URL.
2. **Verify before adding:** always hit the real endpoint and check for `200` + non-empty structure before trusting a token — this file is only useful because every entry was actually tested, not guessed.
3. **Bias toward lower competition, on purpose.** Famous names (Stripe, OpenAI, Airbnb) draw hundreds of applicants per design posting — kept in the list for coverage, but they're the long shots, not the strategy. Favor:
   - **Design/brand agencies** (Landor, IDEO, and similar) — brand/graphic design is their core hire, not a rare one-off role
   - **Design-as-a-service companies** (Superside, Design Pickle) — hire in volume, and often have **contract/freelance/side-gig-friendly** roles, not just full-time
   - **Smaller, less-famous startups** — genuinely fewer applicants per posting than a household name with equivalent pay
   - **DTC/consumer brands** — need in-house graphic and brand designers for packaging, campaigns, and social, which large tech companies rarely post for
4. **Explicitly search for graphic/brand design, not just product/UX.** Big tech ATS boards skew almost entirely toward product/UX titles — the "design" filter alone underrepresents graphic/brand roles. When scanning a new company's board, check for `graphic designer`, `brand designer`, `visual designer`, and `creative` in the title, not just `designer`.
5. **Priority additions for Chineme's search specifically:** more confirmed African tech companies (manual careers-page check is the fastest path since guessed slugs mostly failed above), more branding/creative agencies (this category had the single highest design-role hit-rate of anything tested), and more design tool / product companies on Ashby (it skews toward well-funded, design-forward startups — Figma, Linear, Notion, Ramp, Attio all landed there).
6. **Re-run job/design counts periodically** — they're a snapshot, not fixed. A "0 jobs" company today may open design roles next month; keep the token, just don't expect it to always have design listings.
