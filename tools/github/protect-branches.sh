#!/usr/bin/env bash
# Applique la stratégie de branches de Ydash v2 (ticket D02) via l'API GitHub.
# Prérequis : gh CLI authentifié avec un compte administrateur du dépôt.
#   ./tools/github/protect-branches.sh [owner/repo]
set -euo pipefail

REPO="${1:-jmarvillier/ydash}"
CI_CHECK="build-test"         # job du workflow ci.yml (affiché « ci / build-test »)
TITLE_CHECK="conventional-title" # job du workflow pr-title.yml

echo "→ Réglages de fusion du dépôt $REPO"
gh api -X PATCH "repos/$REPO" \
  -f default_branch=master \
  -F allow_squash_merge=true \
  -F allow_merge_commit=true \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_auto_merge=true \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=PR_BODY >/dev/null

protect() {
  local branch="$1" linear="$2"
  echo "→ Protection de $branch (historique linéaire : $linear)"
  gh api -X PUT "repos/$REPO/branches/$branch/protection" \
    -H "Accept: application/vnd.github+json" \
    --input - >/dev/null <<JSON
{
  "required_status_checks": { "strict": true, "contexts": ["$CI_CHECK", "$TITLE_CHECK"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": $linear,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
}

# develop : squash uniquement → historique linéaire.
protect develop true
# master : reçoit des merge commits develop → master (et les PRs de release) → pas de linéarité imposée.
protect master false

echo "✓ Protections appliquées. Vérifier : https://github.com/$REPO/settings/branches"
