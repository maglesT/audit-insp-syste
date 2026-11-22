Test stand-ins for the Medhanta platform (used by scripts/test-platform.sh):
- cluster.sql, database.sql: copied unchanged from the platform release (medhanta rel-170 db/server/), what init.sh
  runs per database: owner role, app login, report + platform schemas, platform.set_link (PL-08 link switch).
- identity.sql, master_data.sql: minimal stand-ins with the SAME report view columns as core
  (report.employee_v1; report.room_v1 / equipment_v1 / product_v1). Not core's real tables.
