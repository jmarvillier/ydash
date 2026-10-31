#!/usr/bin/env bash
# Active GitHub Pages en mode « GitHub Actions » et autorise master ET develop à déployer
# sur l'environnement github-pages (ticket D05). Compte admin requis.
#   ./tools/github/setup-pages.sh [owner/repo]
set -euo pipefail
REPO="${1:-jmarvillier/ydash}"

echo "→ Pages (source : GitHub Actions)"
gh api -X POST "repos/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 ||
  gh api -X PUT "repos/$REPO/pages" -f build_type=workflow >/dev/null

echo "→ Environnement github-pages : branches autorisées"
gh api -X PUT "repos/$REPO/environments/github-pages" --input - >/dev/null <<'JSON'
{ "deployment_branch_policy": { "protected_branches": false, "custom_branch_policies": true } }
JSON
for branch in master develop; do
  gh api -X POST "repos/$REPO/environments/github-pages/deployment-branch-policies" \
    -f name="$branch" -f type=branch >/dev/null 2>&1 || true
  echo "  + $branch"
done

echo "→ Variables d'environnement (à compléter quand les Functions existent)"
for v in VITE_API_BASE_PROD VITE_API_BASE_STAGING; do
  gh variable list --repo "$REPO" | grep -q "^$v" || echo "  ! $v non définie (gh variable set $v --repo $REPO --body <url>)"
done
echo "✓ https://github.com/$REPO/settings/pages"
