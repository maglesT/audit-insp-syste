-- Medhanta Audit Checklist on the Medhanta platform: its own database "audit" (runs as audit_owner; the app login is
-- audit_app). Regulation text is never stored here: templates and audits keep only item ids, reasons, answers, the
-- customer's own company items, and the people / rooms / equipment / products picked from core (id + display values
-- as at saving, PL-07). People are core's (identity): users is only the id map, made at first sign-on (PL-01).

-- One row: the site this installation belongs to (the platform's site = the "company" of the standalone version).
create table companies (
  id int primary key check (id = 1),
  name text not null check (btrim(name) <> '')
);
insert into companies values (1, 'Site');

create table users (
  id bigint generated always as identity primary key,
  company_id int not null default 1 references companies,
  employee_id uuid not null unique,                 -- core employee id (the token's sub)
  login text not null,
  name text not null,
  created_at timestamptz not null default now(),
  last_login_at timestamptz
);

-- Current state only (a session ends = row deleted). Only a hash of the session id is stored.
create table sessions (
  id text primary key,
  user_id bigint not null references users,
  permissions text[] not null default '{}',         -- this product's codes from core's token, nothing else
  refresh_token text,
  id_token text,
  checked_at timestamptz not null default now(),    -- permissions renewed from core at least every 5 minutes
  last_seen_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table templates (
  id bigint generated always as identity primary key,
  company_id int not null default 1 references companies,
  name text not null,
  config jsonb not null,
  data_version text not null,
  created timestamptz not null default now(),
  updated timestamptz not null default now(),
  updated_by text not null
);

create table audits (
  id bigint generated always as identity primary key,
  company_id int not null default 1 references companies,
  template_id bigint,                               -- kept when the template is deleted
  template_name text not null,
  name text not null,
  site text,
  auditor text,                                     -- display: the auditors' names
  audit_date text,
  header jsonb not null default '{}',               -- auditors, auditees, rooms: id + values as at saving (PL-07)
  status text not null default 'open' check (status in ('open', 'closed')),
  config jsonb not null,
  answers jsonb not null default '{}',              -- finding links: id + values as at saving (PL-07)
  data_version text not null,
  created timestamptz not null default now(),
  updated timestamptz not null default now(),
  updated_by text not null
);

-- Audit trail: who did what, when (insert-only, PL-06).
create table audit_trail (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  user_id bigint references users,
  user_name text not null,
  action text not null,
  object_type text not null,
  object_id bigint,
  detail jsonb
);
create function refuse_change() returns trigger language plpgsql set search_path = pg_catalog, pg_temp as $$
begin
  raise exception '% is insert-only', tg_table_name using errcode = 'insufficient_privilege';
end $$;
create trigger audit_trail_insert_only before update or delete or truncate on audit_trail
  for each statement execute function refuse_change();

-- Least privilege (D-17): the platform gives audit_app SELECT and INSERT; these rows hold current state the app
-- changes or removes. audit_trail and companies stay insert-only / read-only for the app.
do $$
begin
  if exists (select from pg_roles where rolname = 'audit_app') then
    grant update (name, login, last_login_at) on users to audit_app;
    grant update, delete on sessions to audit_app;
    grant update, delete on templates to audit_app;
    grant update, delete on audits to audit_app;
    revoke update, delete, truncate on audit_trail, companies from audit_app;
  end if;
end $$;
