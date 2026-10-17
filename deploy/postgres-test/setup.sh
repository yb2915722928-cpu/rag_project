#!/usr/bin/env bash
# Provision the isolated PostgreSQL test service on the Netcatty Linux host.
# Idempotent for the container/network; never touches the legacy
# /opt/rag-story-1-1/postgres directory, never publishes a non-loopback port.
set -euo pipefail

BASE=/opt/rag-story-1-1/postgres-test
DATA=$BASE/data
SECRETS=$BASE/secrets
EVIDENCE=$BASE/evidence
LOGS=$BASE/logs
CONTAINER=rag-story-1-1-postgres-test
NETWORK=rag-story-1-1-test
# Digest-pinned identity: every inspect and run below uses a digest reference,
# never a bare tag. The image ID form is accepted because an offline
# docker-load keeps the reviewed content under that ID.
IMAGE_DIGEST=sha256:2358fcba361ed2233a5ed81b5fe4ca779ccb304120ce531a3bf51c0ed7e2bc11
IMAGE_REF=pgvector/pgvector:0.8.7-pg18-bookworm@$IMAGE_DIGEST
IMAGE=
if docker image inspect "$IMAGE_REF" >/dev/null 2>&1; then
  IMAGE=$IMAGE_REF
elif docker image inspect "$IMAGE_DIGEST" >/dev/null 2>&1; then
  IMAGE=$IMAGE_DIGEST
else
  echo "blocked: digest-pinned image is not present locally: $IMAGE_REF" >&2
  exit 2
fi

HOST_PORT=55432
PG_UID=999
PG_GID=999
TEST_ROLE=rag_test

fail() {
  echo "blocked: $*" >&2
  exit 2
}

umask 077
mkdir -p "$DATA" "$SECRETS" "$EVIDENCE" "$LOGS"
chown "$PG_UID:$PG_GID" "$DATA"
chmod 0700 "$DATA"
chown root:root "$SECRETS"
chmod 0700 "$SECRETS"

# Generate credentials once; never print them and never rewrite an existing file.
if [ ! -s "$SECRETS/postgres-password" ]; then
  openssl rand -hex 24 > "$SECRETS/postgres-password"
fi
if [ ! -s "$SECRETS/test-role-password" ]; then
  openssl rand -hex 24 > "$SECRETS/test-role-password"
fi
chown "$PG_UID:$PG_GID" "$SECRETS/postgres-password"
chmod 0400 "$SECRETS/postgres-password"
chown root:root "$SECRETS/test-role-password"
chmod 0400 "$SECRETS/test-role-password"

if [ "$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "$IMAGE")" != "linux/amd64" ]; then
  fail "image platform is not linux/amd64"
fi

# The service is published only on 127.0.0.1, so an ordinary project bridge is
# required. An internal network would silently disable port publishing, so a
# mismatching existing network is refused rather than modified.
if docker network inspect "$NETWORK" >/dev/null 2>&1; then
  if [ "$(docker network inspect --format '{{.Internal}}' "$NETWORK")" = "true" ]; then
    fail "existing network $NETWORK is internal; refusing to modify it"
  fi
fi
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
  docker network create --driver bridge "$NETWORK" >/dev/null
fi

if ! docker container inspect "$CONTAINER" >/dev/null 2>&1; then
  docker run --detach \
    --name "$CONTAINER" \
    --hostname "$CONTAINER" \
    --network "$NETWORK" \
    --network-alias postgres-test \
    --publish "127.0.0.1:$HOST_PORT:5432" \
    --platform linux/amd64 \
    --pull never \
    --user "$PG_UID:$PG_GID" \
    --restart "no" \
    --stop-signal SIGINT \
    --stop-timeout 60 \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=16m,mode=1777 \
    --tmpfs /var/run/postgresql:rw,noexec,nosuid,size=4m,mode=0777 \
    --mount type=bind,src="$DATA",dst=/var/lib/postgresql \
    --mount type=bind,src="$SECRETS/postgres-password",dst=/run/secrets/postgres_password,readonly \
    --env POSTGRES_DB=rag \
    --env POSTGRES_USER=rag \
    --env POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password \
    --env PGDATA=/var/lib/postgresql/18/docker \
    --pids-limit 256 \
    --memory 1g \
    --shm-size 256m \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --log-driver json-file \
    --log-opt max-size=5m \
    --log-opt max-file=2 \
    "$IMAGE" >/dev/null
fi

# Wait for readiness without printing credentials.
for _ in $(seq 1 60); do
  if docker exec "$CONTAINER" pg_isready -h /var/run/postgresql -p 5432 -U rag -d rag >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker exec "$CONTAINER" pg_isready -h /var/run/postgresql -p 5432 -U rag -d rag >/dev/null 2>&1 ||
  fail "PostgreSQL did not become ready"

# The password reaches psql through the docker-exec client environment and
# psql's \getenv, never through argv of any process.
RAG_TEST_ROLE_PASSWORD="$(cat "$SECRETS/test-role-password")" \
  docker exec -e RAG_TEST_ROLE_PASSWORD -i "$CONTAINER" \
  psql -v ON_ERROR_STOP=1 -U rag -d rag >"$LOGS/provision-sql.log" 2>&1 <<'SQL'
\getenv role_password RAG_TEST_ROLE_PASSWORD
SELECT 'CREATE EXTENSION IF NOT EXISTS vector'
WHERE NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')\gexec
SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L',
              'rag_test', :'role_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rag_test')\gexec
ALTER ROLE rag_test LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
SELECT format('ALTER ROLE %I PASSWORD %L', 'rag_test', :'role_password')\gexec
GRANT CONNECT, CREATE ON DATABASE rag TO rag_test;
GRANT USAGE ON SCHEMA public TO rag_test;
SQL
unset RAG_TEST_ROLE_PASSWORD

# Assert the real versions before handing the connection over.
SERVER_VERSION_NUM=$(docker exec "$CONTAINER" psql -At -U rag -d rag -c "SHOW server_version_num")
if [ "$SERVER_VERSION_NUM" != "180006" ]; then
  fail "unexpected PostgreSQL server_version_num: $SERVER_VERSION_NUM"
fi
VECTOR_VERSION=$(docker exec "$CONTAINER" psql -At -U rag -d rag -c "SELECT extversion FROM pg_extension WHERE extname='vector'")
if [ "$VECTOR_VERSION" != "0.8.7" ]; then
  fail "unexpected vector extension version: $VECTOR_VERSION"
fi

# Prove the loopback-only path works with the test role; the container is
# short-lived and is removed by --rm.
PGPASSWORD="$(cat "$SECRETS/test-role-password")" \
  docker run --rm --network host --pull never \
    --env PGPASSWORD --env PGSSLMODE=disable \
    --entrypoint psql "$IMAGE" \
    -h 127.0.0.1 -p "$HOST_PORT" -U "$TEST_ROLE" -d rag -At \
    -c "SELECT current_user || '|' || current_database() || '|' || current_setting('server_version_num') || '|' || (SELECT extversion FROM pg_extension WHERE extname='vector')" \
    >"$LOGS/loopback-role-check.log" 2>&1 ||
  fail "loopback connection with the restricted role failed"
LOOPBACK_RESULT=$(cat "$LOGS/loopback-role-check.log")
if [ "$LOOPBACK_RESULT" != "rag_test|rag|180006|0.8.7" ]; then
  fail "unexpected loopback connection result: $LOOPBACK_RESULT"
fi

# Connection hand-off file: sourced, never passed on argv or echoed.
test_password=$(cat "$SECRETS/test-role-password")
cat > "$SECRETS/test-database.env" <<EOF
# Source this file in the backend test shell; do not print or commit it.
export RAG_TEST_DATABASE_URL='postgresql+psycopg://$TEST_ROLE:$test_password@127.0.0.1:$HOST_PORT/rag'
export RAG_TEST_ALLOW_SCHEMA_CREATE=1
EOF
unset test_password
chown root:root "$SECRETS/test-database.env"
chmod 0400 "$SECRETS/test-database.env"

python3 - "$BASE" "$CONTAINER" "$NETWORK" "$IMAGE" <<'PY'
import json, subprocess, sys
from pathlib import Path

base, container, network, image = sys.argv[1:5]
base = Path(base)

def run(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()

def sql(query):
    return run("docker", "exec", container, "psql", "-At", "-U", "rag", "-d", "rag",
               "-c", query)

inspect = json.loads(run("docker", "image", "inspect", image))[0]
container_json = json.loads(run("docker", "container", "inspect", container))[0]
net = json.loads(run("docker", "network", "inspect", network))[0]
data = base / "data"
stat = data.stat()
findmnt = run("findmnt", "-T", str(data), "-n", "-o", "FSTYPE,SOURCE,TARGET")
listeners = run("bash", "-c", "ss -ltnH | grep -F ':55432' || true")
payload = {
    "recorded_at_utc": run("date", "-u", "+%Y-%m-%dT%H:%M:%SZ"),
    "purpose": "Story 1.1 AC2 isolated real PostgreSQL test service",
    "image": {
        "reference": image,
        "id": inspect["Id"],
        "repo_digests": inspect.get("RepoDigests"),
        "created": inspect.get("Created"),
        "os": inspect["Os"],
        "architecture": inspect["Architecture"],
        "layer_count": len(inspect["RootFS"]["Layers"]),
        "layers": inspect["RootFS"]["Layers"],
        "env_version_marker": [e for e in inspect["Config"]["Env"] if e.startswith("PG_VERSION=")],
    },
    "container": {
        "name": container,
        "id": container_json["Id"],
        "image_id": container_json["Image"],
        "restart_policy": container_json["HostConfig"].get("RestartPolicy"),
        "read_only_rootfs": container_json["HostConfig"].get("ReadonlyRootfs"),
        "cap_drop": container_json["HostConfig"].get("CapDrop"),
        "security_opt": container_json["HostConfig"].get("SecurityOpt"),
        "pids_limit": container_json["HostConfig"].get("PidsLimit"),
        "memory": container_json["HostConfig"].get("Memory"),
        "binds": container_json["HostConfig"].get("Binds"),
        "port_bindings": container_json["HostConfig"].get("PortBindings"),
        "user": container_json["Config"].get("User"),
    },
    "network": {
        "name": net["Name"],
        "driver": net["Driver"],
        "internal": net.get("Internal"),
        "id": net["Id"],
    },
    "versions": {
        "server_version": sql("SHOW server_version"),
        "server_version_num": sql("SHOW server_version_num"),
        "vector_extversion": sql("SELECT extversion FROM pg_extension WHERE extname='vector'"),
        "vector_default_version": sql(
            "SELECT default_version FROM pg_available_extensions WHERE name='vector'"),
        "vector_extension_schema": sql(
            "SELECT n.nspname FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace "
            "WHERE e.extname='vector'"),
        "test_role": sql("SELECT rolname FROM pg_roles WHERE rolname='rag_test'"),
        "test_role_superuser": sql(
            "SELECT rolsuper FROM pg_roles WHERE rolname='rag_test'"),
    },
    "data_directory": {
        "path": str(data),
        "uid": stat.st_uid,
        "gid": stat.st_gid,
        "mode": oct(stat.st_mode & 0o777),
        "findmnt": findmnt,
        "on_object_storage": findmnt.startswith("cosfs"),
    },
    "listeners": listeners.splitlines(),
    "secrets": {
        "postgres_password_file": str(base / "secrets" / "postgres-password"),
        "test_role_password_file": str(base / "secrets" / "test-role-password"),
        "test_env_file": str(base / "secrets" / "test-database.env"),
        "values_recorded": False,
    },
    "limitations": [
        "Image layers arrived through the Tencent Cloud official mirror used by the "
        "daemon; the digest is the publish-side official digest, not a direct "
        "container-registry pull.",
        "This service is a test fixture only; it is not the production D deployment.",
    ],
}
(base / "evidence" / "postgres-test-environment.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "container": payload["container"]["name"],
    "container_id": payload["container"]["id"][:12],
    "network": payload["network"]["name"],
    "versions": payload["versions"],
    "data_directory": payload["data_directory"],
    "listeners": payload["listeners"],
}, indent=2))
PY

mkdir -p /fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment
cp "$EVIDENCE/postgres-test-environment.json" \
   /fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment/
cp "$LOGS/provision-sql.log" "$LOGS/loopback-role-check.log" \
   /fileOfRag/testOfRAG/metadata/story-1-1/postgres-test-environment/

echo "provisioning complete; credentials remain in $SECRETS (values not printed)"
