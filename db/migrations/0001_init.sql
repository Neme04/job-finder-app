-- Phase 1: core schema + RLS per CLAUDE.md §5
-- Run via Supabase SQL editor or `supabase db push`.

create extension if not exists "pgcrypto";

-- ============================================================
-- profiles
-- ============================================================
create table if not exists profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  role text not null default 'user' check (role in ('user', 'admin')),
  full_name text,
  notify_email boolean not null default true,
  notify_whatsapp boolean not null default false,
  created_at timestamptz not null default now()
);

alter table profiles enable row level security;

create policy "profiles: read own"
  on profiles for select
  using (auth.uid() = user_id);

create policy "profiles: update own"
  on profiles for update
  using (auth.uid() = user_id);

create policy "profiles: insert own"
  on profiles for insert
  with check (auth.uid() = user_id);

-- ============================================================
-- search_criteria
-- ============================================================
create table if not exists search_criteria (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (user_id) on delete cascade,
  job_titles text[] not null default '{}',
  regions text[] not null default '{}',
  remote_pref text check (remote_pref in ('remote', 'hybrid', 'onsite', 'any')) default 'any',
  salary_floor numeric,
  currency text default 'USD',
  sources_enabled text[] not null default '{}',
  updated_at timestamptz not null default now()
);

alter table search_criteria enable row level security;

create policy "search_criteria: read own"
  on search_criteria for select
  using (auth.uid() = profile_id);

create policy "search_criteria: write own"
  on search_criteria for all
  using (auth.uid() = profile_id)
  with check (auth.uid() = profile_id);

-- ============================================================
-- jobs (shared, deduped global pool)
-- ============================================================
create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  canonical_key text not null,
  source_id text not null,
  external_id text not null,
  title text not null,
  company text not null,
  location text,
  remote boolean not null default false,
  description text,
  apply_url text not null,
  salary_min numeric,
  salary_max numeric,
  currency text,
  posted_at timestamptz,
  first_seen timestamptz not null default now(),
  last_seen timestamptz not null default now(),
  unique (source_id, external_id)
);

create index if not exists jobs_last_seen_idx on jobs (last_seen);
create index if not exists jobs_canonical_key_idx on jobs (canonical_key);

alter table jobs enable row level security;

create policy "jobs: shared read"
  on jobs for select
  using (true);

-- writes to jobs happen only via the engine's service key, which bypasses RLS.

-- ============================================================
-- user_jobs (per-user layer)
-- ============================================================
create table if not exists user_jobs (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles (user_id) on delete cascade,
  job_id uuid not null references jobs (id) on delete cascade,
  status text not null default 'new' check (status in ('new', 'saved', 'applied', 'skipped')),
  notified_at timestamptz,
  created_at timestamptz not null default now(),
  unique (profile_id, job_id)
);

alter table user_jobs enable row level security;

create policy "user_jobs: read own"
  on user_jobs for select
  using (auth.uid() = profile_id);

create policy "user_jobs: write own"
  on user_jobs for all
  using (auth.uid() = profile_id)
  with check (auth.uid() = profile_id);

-- inserts of new matches happen via the engine's service key (bypasses RLS);
-- users may only update status on rows visible to them.
