-- =============================================================================
-- RepurposeAI — Supabase schema (fresh project)
-- Run this ONCE in the Supabase SQL editor:
--   Dashboard → SQL Editor → New query → paste this → Run
-- Safe to re-run (uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).
-- =============================================================================

-- 1) Users table — id is the Google 'sub' claim (permanent user ID)
create table if not exists users (
  id text primary key,
  email text unique not null,
  name text,
  picture text,
  created_at timestamptz not null default now(),
  last_login_at timestamptz not null default now()
);

-- 2) Tasks table (only created if missing — matches models.py schema)
create table if not exists tasks (
  id text primary key,
  user_id text,
  status text not null default 'Pending',
  input_type text,
  input_data text,
  results jsonb,
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 3) Link tasks to users (safe on fresh DB and on old DBs without the column)
alter table tasks
  add column if not exists user_id text references users(id) on delete cascade;

create index if not exists idx_tasks_user_id on tasks(user_id);
create index if not exists idx_tasks_user_created on tasks(user_id, created_at desc);

-- 4) Auto-update last_login_at when a user row is updated
create or replace function touch_last_login()
returns trigger as $$
begin
  new.last_login_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_touch_last_login on users;
create trigger trg_touch_last_login
  before update on users
  for each row execute function touch_last_login();
