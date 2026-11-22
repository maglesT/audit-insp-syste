-- Stand-in for core's identity database (runs as identity_owner). Same report.employee_v1 columns as core.
create table employee (id uuid primary key default gen_random_uuid(), login text not null unique, full_name text not null,
  active boolean not null default true, changed_at timestamptz not null default now());
create view report.employee_v1 with (security_barrier) as
select id, login, full_name, active, now() as read_at, changed_at as data_as_of from employee;
revoke all on report.employee_v1 from public;
