#!/usr/bin/env bash
# Monitoring minimal Ydash v2 (ticket D11) : métriques basées sur les logs structurés des Functions
# (functions/src/logger.ts) + 2 alertes Cloud Monitoring envoyées par e-mail. Idempotent.
#   ./infra/monitoring/setup-monitoring.sh <email> [project]
set -euo pipefail

EMAIL="${1:?usage: $0 <email> [project]}"
PROJECT="${2:-dashboard-ydash}"
DIR="$(cd "$(dirname "$0")" && pwd)"

metric() {
  local name="$1" event="$2" desc="$3"
  local filter="resource.type=\"cloud_run_revision\" AND jsonPayload.event=\"$event\""
  local config
  config=$(mktemp)
  cat >"$config" <<YAML
name: $name
description: $desc
filter: '$filter'
metricDescriptor:
  metricKind: DELTA
  valueType: INT64
  labels:
    - key: env
      valueType: STRING
labelExtractors:
  env: EXTRACT(jsonPayload.env)
YAML
  if gcloud logging metrics describe "$name" --project "$PROJECT" >/dev/null 2>&1; then
    gcloud logging metrics update "$name" --project "$PROJECT" --config-from-file "$config" >/dev/null
  else
    gcloud logging metrics create "$name" --project "$PROJECT" --config-from-file "$config" >/dev/null
  fi
  rm -f "$config"
  echo "  métrique $name"
}

echo "→ Métriques basées sur les logs"
metric ydash_sync_errors sync.error "Synchronisations OKX en erreur (par env)"
metric ydash_sync_success sync.success "Synchronisations OKX réussies (par env)"

echo "→ Canal de notification e-mail"
CHANNEL=$(gcloud beta monitoring channels list --project "$PROJECT" \
  --filter "type=\"email\" AND labels.email_address=\"$EMAIL\"" --format 'value(name)' | head -n1)
if [[ -z "$CHANNEL" ]]; then
  CHANNEL=$(gcloud beta monitoring channels create --project "$PROJECT" --type email \
    --display-name "Ydash alertes" --channel-labels "email_address=$EMAIL" --format 'value(name)')
fi
echo "  $CHANNEL"

echo "→ Politiques d'alerte"
for policy in "$DIR"/policy-*.json; do
  name=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["displayName"])' "$policy")
  existing=$(gcloud alpha monitoring policies list --project "$PROJECT" \
    --filter "displayName=\"$name\"" --format 'value(name)' | head -n1)
  tmp=$(mktemp)
  sed "s#__CHANNEL__#$CHANNEL#" "$policy" >"$tmp"
  if [[ -n "$existing" ]]; then
    gcloud alpha monitoring policies update "$existing" --project "$PROJECT" --policy-from-file "$tmp" >/dev/null
  else
    gcloud alpha monitoring policies create --project "$PROJECT" --policy-from-file "$tmp" >/dev/null
  fi
  rm -f "$tmp"
  echo "  $name"
done
echo "✓ https://console.cloud.google.com/monitoring/alerting?project=$PROJECT"
