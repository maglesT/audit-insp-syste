-- MED-11 (PL-06): an audit record is never deleted. An open audit is withdrawn with a reason and kept; a closed audit
-- is final. The app login loses DELETE on audits.
alter table audits drop constraint audits_status_check;
alter table audits add constraint audits_status_check check (status in ('open', 'closed', 'withdrawn'));
alter table audits add column withdrawn_reason text;
alter table audits add constraint audits_withdrawn_reason check (status <> 'withdrawn' or btrim(coalesce(withdrawn_reason, '')) <> '');

do $$
begin
  if exists (select from pg_roles where rolname = 'audit_app') then
    revoke delete on audits from audit_app;
  end if;
end $$;
