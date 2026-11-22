-- Stand-in for core's master_data database (runs as master_data_owner). Same leading report view columns as core.
create table item (id uuid primary key default gen_random_uuid(), kind text not null, code text not null unique, name text not null,
  version int not null default 1, active boolean not null default true, changed_at timestamptz not null default now());
create view report.room_v1 with (security_barrier) as
select id, code, name, version, active, null::text as area, null::text as grade, now() as read_at, changed_at as data_as_of from item where kind = 'room';
create view report.equipment_v1 with (security_barrier) as
select id, code, name, version, active, null::text as type, now() as read_at, changed_at as data_as_of from item where kind = 'equipment';
create view report.product_v1 with (security_barrier) as
select id, code, name, version, active, null::text as strength, now() as read_at, changed_at as data_as_of from item where kind = 'product';
revoke all on report.room_v1, report.equipment_v1, report.product_v1 from public;
