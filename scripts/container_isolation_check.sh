#!/usr/bin/env bash
# Run the documented isolation recipe against the bundled demo repository and verify the outcome.
#
#   docker build -t reposcan:local . && scripts/container_isolation_check.sh reposcan:local
#
# Expects: exit code 1 (policy failure on the intentionally vulnerable repo), 6 findings, every
# scanner "ok", and proof that the container really has no network.
set -u
IMAGE="${1:?usage: container_isolation_check.sh IMAGE}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
# Run as the caller's own (non-root) uid: reposcan writes reports with mode 0600, so the files in
# $OUT are then owned by, and readable to, the person who started the scan.
ISOLATION=(--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges
           --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=256m)

echo "== 1. the container has no network"
docker run "${ISOLATION[@]}" --entrypoint python "$IMAGE" -c "
import socket, sys
try:
    socket.create_connection(('1.1.1.1', 53), timeout=3)
except OSError:
    sys.exit(0)
sys.exit(1)"
[ $? -eq 0 ] || { echo "FAIL: the container could reach the network"; exit 1; }
echo "   ok: connection attempt failed"

echo "== 2. scan the demo repository (read-only mount)"
docker run "${ISOLATION[@]}" \
  -v "$ROOT/sample-data/demo-repo:/src:ro" -v "$OUT:/out" \
  "$IMAGE" scan /src --scanners gitleaks,semgrep --output-dir /out --format json
code=$?
[ "$code" -eq 1 ] || { echo "FAIL: expected exit 1, got $code"; exit 1; }
echo "   ok: exit code 1"

echo "== 3. verify the report"
python3 - "$OUT/reposcan-report.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
statuses = {s["name"]: s["status"] for s in data["scanners"]}
assert statuses == {"gitleaks": "ok", "semgrep": "ok"}, statuses
assert data["summary"]["total"] == 6, data["summary"]
text = json.dumps(data)
assert "AAAABBBBCCCCDDDDEEEEFFFF" not in text and "q7Xk2vR9mTz4WbN8pLc3YdHs6JfGa1Ue" not in text
print("   ok: 6 findings, both scanners ok, no secret values in the report")
PY
