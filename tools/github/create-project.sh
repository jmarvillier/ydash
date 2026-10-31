#!/usr/bin/env bash
# Crée le GitHub Project « Ydash v2 » et y rattache toutes les issues du dépôt (ticket D03).
# Prérequis : gh CLI authentifié avec le scope `project` (gh auth refresh -s project).
#   ./tools/github/create-project.sh [owner] [repo]
# Les vues « Board par milestone » et « Table » se configurent ensuite dans l'UI
# (l'API GraphQL ne permet pas encore de créer des vues).
set -euo pipefail

OWNER="${1:-jmarvillier}"
REPO="${2:-ydash}"
TITLE="Ydash v2"

number=$(gh project list --owner "$OWNER" --format json --jq ".projects[] | select(.title==\"$TITLE\") | .number" | head -n1)
if [[ -z "$number" ]]; then
  echo "→ Création du projet « $TITLE »"
  number=$(gh project create --owner "$OWNER" --title "$TITLE" --format json --jq '.number')
fi
echo "→ Projet #$number"
gh project link "$number" --owner "$OWNER" --repo "$OWNER/$REPO" || true

echo "→ Rattachement des issues"
gh issue list --repo "$OWNER/$REPO" --state all --limit 500 --json url --jq '.[].url' |
  while read -r url; do
    gh project item-add "$number" --owner "$OWNER" --url "$url" >/dev/null && echo "  + $url"
  done

echo "✓ https://github.com/users/$OWNER/projects/$number"
echo "  Ajouter les vues : Board groupé par Milestone, Table (Status, Labels, Milestone)."
