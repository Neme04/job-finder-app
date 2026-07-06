-- Fixes a 409 Conflict on the sweep's upsert: ON CONFLICT (source_id, external_id)
-- doesn't cover the separate canonical_key unique constraint, so any insert whose
-- canonical_key collides with a different (source_id, external_id) row (e.g. a
-- reposted listing with a new external_id) fails outright instead of merging.
-- In-run duplicate canonical_keys are already collapsed by engine/dedupe before
-- the write, so the DB-level uniqueness here is redundant — keep the index for
-- lookups, drop the constraint.

alter table jobs drop constraint if exists jobs_canonical_key_key;
