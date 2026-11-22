#!/usr/bin/env bash
# Platform tests (PL-01, PL-07, PL-08): a throwaway postgres:17 container (tmpfs, removed afterwards), set up like the
# platform's init.sh (cluster.sql + database.sql per database), the audit migrations applied as audit_owner, stand-ins
# for identity and master_data, then node --test test/platform/platform.test.js. Never touches any other database.
set -euo pipefail
cd "$(dirname "$0")/.."
NAME=audit-pgtest
PORT=${PGTEST_PORT:-$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')}
PW=$(openssl rand -hex 16)
APW=$(openssl rand -hex 16)
docker rm -f $NAME >/dev/null 2>&1 || true
trap 'docker rm -f $NAME >/dev/null 2>&1 || true' EXIT
docker run -d --rm --name $NAME -e POSTGRES_PASSWORD="$PW" -p 127.0.0.1:$PORT:5432 --tmpfs /var/lib/postgresql/data postgres:17 >/dev/null
for i in $(seq 1 60); do docker exec $NAME pg_isready -U postgres -h 127.0.0.1 >/dev/null 2>&1 && break; sleep 1; done
sleep 1
psql_() { docker exec -i $NAME psql -X -q -v ON_ERROR_STOP=1 -U postgres "$@"; }
setup() { # db app
  psql_ -d postgres -v db="$1" -v owner="$1_owner" -v app="$2" < test/platform/cluster.sql
  psql_ -d "$1" -v db="$1" -v owner="$1_owner" -v app="$2" < test/platform/database.sql
}
setup identity core_app
setup master_data core_app
setup audit audit_app
psql_ -d identity -c "set role identity_owner" -f - < test/platform/identity.sql
psql_ -d master_data -c "set role master_data_owner" -f - < test/platform/master_data.sql
psql_ -d postgres -c "alter role audit_app login password '$APW'"
export PGTEST_SU="postgres://postgres:$PW@127.0.0.1:$PORT"
export PGTEST_APP="postgres://audit_app:$APW@127.0.0.1:$PORT"
node --no-warnings --test --test-concurrency=1 test/platform/platform.test.js
