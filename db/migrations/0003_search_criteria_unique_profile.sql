-- Search criteria is a single, editable-anytime set per user (CLAUDE.md §3:
-- "the only setup"). The frontend upserts on profile_id, which requires a
-- unique constraint for ON CONFLICT to target.

alter table search_criteria add constraint search_criteria_profile_id_key unique (profile_id);
