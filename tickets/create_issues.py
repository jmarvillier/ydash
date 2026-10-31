#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crée labels, milestones et issues du backlog initial sur GitHub (via `gh api`),
puis résout les références {{KEY}} en #numéro et génère docs/BACKLOG.md.

Usage :
  python3 tickets/create_issues.py --repo jmarvillier/ydash [--dry-run] [--state tickets/state.json]

Idempotent : l'état (clé → numéro) est conservé dans state.json ; une issue déjà créée
n'est pas recréée (son corps est re-synchronisé si --update).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tickets  # noqa: E402

REF = re.compile(r"\{\{([A-Z0-9-]+)\}\}")


def gh(args, payload=None, method=None, quiet=False):
    cmd = ["gh", "api"]
    if method:
        cmd += ["--method", method]
    cmd += args
    if payload is not None:
        cmd += ["--input", "-"]
        data = json.dumps(payload).encode("utf-8")
    else:
        data = None
    r = subprocess.run(cmd, input=data, capture_output=True)
    if r.returncode != 0:
        if not quiet:
            sys.stderr.write(f"gh api {' '.join(args)} → {r.stderr.decode()}\n")
        raise RuntimeError(r.stderr.decode())
    out = r.stdout.decode()
    return json.loads(out) if out.strip() else None


def ensure_labels(repo, dry):
    existing = {l["name"]: l for l in gh([f"repos/{repo}/labels", "--paginate"])}
    for name, color, desc in tickets.LABELS:
        if name in existing:
            cur = existing[name]
            if cur.get("color") != color or (cur.get("description") or "") != desc:
                print(f"  ~ label {name}")
                if not dry:
                    gh([f"repos/{repo}/labels/{name}"], {"color": color, "description": desc}, "PATCH")
        else:
            print(f"  + label {name}")
            if not dry:
                gh([f"repos/{repo}/labels"], {"name": name, "color": color, "description": desc}, "POST")


def ensure_milestones(repo, dry):
    existing = {m["title"]: m for m in gh([f"repos/{repo}/milestones", "--paginate", "-f", "state=all"])}
    numbers = {}
    for title, desc in tickets.MILESTONES:
        if title in existing:
            numbers[title] = existing[title]["number"]
            continue
        print(f"  + milestone {title}")
        if dry:
            numbers[title] = 0
        else:
            m = gh([f"repos/{repo}/milestones"], {"title": title, "description": desc}, "POST")
            numbers[title] = m["number"]
            time.sleep(0.5)
    return numbers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--update", action="store_true", help="re-synchronise titre/corps/labels des issues existantes")
    ap.add_argument("--state", default=str(HERE / "state.json"))
    a = ap.parse_args()

    state_path = Path(a.state)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}

    print("Labels…")
    ensure_labels(a.repo, a.dry_run)
    print("Milestones…")
    ms = ensure_milestones(a.repo, a.dry_run)

    keys = [t["key"] for t in tickets.T]
    assert len(keys) == len(set(keys)), "clés dupliquées"
    for t in tickets.T:
        for ref in REF.findall(t["body"]):
            assert ref in keys, f"{t['key']} référence une clé inconnue : {ref}"

    print(f"Issues ({len(tickets.T)})…")
    for t in tickets.T:
        if t["key"] in state:
            continue
        print(f"  + {t['key']} — {t['title']}")
        if a.dry_run:
            state[t["key"]] = 0
            continue
        payload = {"title": t["title"], "body": t["body"], "labels": t["labels"],
                   "milestone": ms[t["milestone"]]}
        for attempt in range(3):
            try:
                issue = gh([f"repos/{a.repo}/issues"], payload, "POST")
                break
            except RuntimeError as e:
                if attempt == 2:
                    raise
                time.sleep(5 * (attempt + 1))
        state[t["key"]] = issue["number"]
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        time.sleep(1.2)  # limite secondaire GitHub (création de contenu)

    print("Résolution des références…")
    for t in tickets.T:
        resolved = REF.sub(lambda m: f"#{state[m.group(1)]}", t["body"])
        if resolved != t["body"] or a.update:
            print(f"  ~ #{state[t['key']]} {t['key']}")
            if not a.dry_run:
                payload = {"body": resolved}
                if a.update:
                    payload.update({"title": t["title"], "labels": t["labels"], "milestone": ms[t["milestone"]]})
                gh([f"repos/{a.repo}/issues/{state[t['key']]}"], payload, "PATCH")
                time.sleep(0.8)

    # BACKLOG.md
    lines = ["# Backlog initial Ydash v2", "",
             f"Généré par `tickets/create_issues.py` depuis `tickets/tickets.py` — {len(tickets.T)} tickets.", ""]
    by_ms = {}
    for t in tickets.T:
        by_ms.setdefault(t["milestone"], []).append(t)
    for title, _ in tickets.MILESTONES:
        lines += [f"## {title}", "", "| # | Clé | Titre | Labels |", "|---|---|---|---|"]
        for t in by_ms.get(title, []):
            n = state.get(t["key"], 0)
            link = f"[#{n}](https://github.com/{a.repo}/issues/{n})" if n else "—"
            lines.append(f"| {link} | `{t['key']}` | {t['title']} | {', '.join(t['labels'])} |")
        lines.append("")
    out = HERE.parent / "docs" / "BACKLOG.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"→ {out}")
    print("Terminé.")


if __name__ == "__main__":
    main()
