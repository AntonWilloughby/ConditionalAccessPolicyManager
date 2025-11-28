#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: security_quickcheck.sh <hostname>

Runs a set of read-only security checks against the given HTTPS hostname and
prints a short report highlighting potential issues.

Examples:
  ./scripts/security_quickcheck.sh my-app.azurewebsites.net
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

HOST="$1"
BASE_URL="https://${HOST}"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT

report_section() {
  echo
  echo "=== $1 ==="
}

check_header() {
  local header_name="$1"
  local headers_file="$2"
  if grep -qi "^${header_name}:" "$headers_file"; then
    echo "[OK] ${header_name} present"
  else
    echo "[WARN] ${header_name} missing"
  fi
}

report_section "Gathering root headers"
root_headers="${TMP_DIR}/root_headers.txt"
curl -sS -D "$root_headers" -o /dev/null "$BASE_URL" || {
  echo "[ERROR] Failed to reach ${BASE_URL}"
  exit 1
}
cat "$root_headers"

report_section "Header summary"
check_header "Strict-Transport-Security" "$root_headers"
check_header "Content-Security-Policy" "$root_headers"
check_header "X-Frame-Options" "$root_headers"
check_header "X-Content-Type-Options" "$root_headers"
check_header "Referrer-Policy" "$root_headers"
if grep -qi '^set-cookie:' "$root_headers"; then
  if grep -qi 'set-cookie: .*HttpOnly' "$root_headers" && \
     grep -qi 'set-cookie: .*Secure' "$root_headers"; then
    echo "[OK] Cookies use HttpOnly + Secure"
  else
    echo "[WARN] Cookies missing HttpOnly and/or Secure"
  fi
else
  echo "[INFO] No cookies returned on root request"
fi

report_section "TLS certificate"
cert_info="${TMP_DIR}/cert.txt"
if openssl s_client -connect "${HOST}:443" -servername "$HOST" < /dev/null 2>"${TMP_DIR}/openssl.log" | \
   openssl x509 -noout -dates -subject > "$cert_info" 2>/dev/null; then
  cat "$cert_info"
else
  echo "[WARN] Unable to retrieve certificate info"
  cat "${TMP_DIR}/openssl.log"
fi

report_section "CORS preflight (OPTIONS)"
options_resp="${TMP_DIR}/options.txt"
curl -sS -i -X OPTIONS "$BASE_URL/" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: GET" > "$options_resp"
cat "$options_resp"

report_section "Sensitive files"
check_file() {
  local path="$1"
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL$path")
  if [[ "$code" == "200" ]]; then
    echo "[CRITICAL] $path returned 200 (publicly accessible)"
  elif [[ "$code" =~ ^(301|302|307|308)$ ]]; then
    echo "[WARN] $path redirected (status $code)"
  else
    echo "[OK] $path -> $code"
  fi
}
check_file "/.env"
check_file "/.git/config"
check_file "/robots.txt"
check_file "/swagger.json"
check_file "/swagger/index.html"

report_section "HTTP methods allowed"
allow_header=$(grep -i '^allow:' "$options_resp" | sed 's/^[Aa]llow: //')
if [[ -n "$allow_header" ]]; then
  echo "Allow: $allow_header"
  if echo "$allow_header" | grep -qiE 'PUT|DELETE|TRACE|PATCH'; then
    echo "[WARN] Uncommon methods exposed on root"
  else
    echo "[OK] Only HEAD/GET/OPTIONS exposed"
  fi
else
  echo "[INFO] No Allow header returned"
fi

echo
echo "Report complete. Review warnings/critical findings above."
