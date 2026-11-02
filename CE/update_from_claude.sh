#!/usr/bin/env bash
# update_from_claude.sh - pull Claude's branch into this folder without losing your edits.
#   bash update_from_claude.sh [branch]        (default: claude/busy-cori-axmdsv)
# 1. backs up references/games (the game databases) to ~/renown_games_backup/<timestamp>
# 2. commits any local edits you have ("local changes <date>")
# 3. merges the branch in. Clean merge: done.
#    Conflict: undoes the merge, pushes your work to the branch "matt-local", and tells you to ask Claude to merge it.
# Stop the board server before running it.
set -u
BRANCH="${1:-claude/busy-cori-axmdsv}"
cd "$(dirname "$0")" || exit 1
ROOT="$(git rev-parse --show-toplevel)" || { echo "not inside the git repo"; exit 1; }
cd "$ROOT" || exit 1

command -v git-lfs >/dev/null 2>&1 || { echo "git-lfs is missing: sudo apt install -y git-lfs && git lfs install"; exit 1; }
git config core.autocrlf true                     # Windows files (CRLF) aren't seen as changed

[ -n "$(git config user.name)" ]  || git config user.name  "mlang95"
[ -n "$(git config user.email)" ] || git config user.email "mattlang95@gmail.com"

# 1. back up the game databases
if [ -d CE/references/games ]; then
  B="$HOME/renown_games_backup/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$B" && cp -r CE/references/games/. "$B"/ && echo "games backed up to $B"
fi

# 2. get onto the branch, committing local edits first
CUR="$(git rev-parse --abbrev-ref HEAD)"
if [ -n "$(git status --porcelain)" ]; then
  git add -A && git commit -q -m "local changes $(date '+%Y-%m-%d %H:%M')" && echo "committed your local changes on $CUR"
fi
git fetch -q origin "$BRANCH" || { echo "fetch failed (network?)"; exit 1; }
if [ "$CUR" != "$BRANCH" ]; then
  if git show-ref -q --verify "refs/heads/$BRANCH"; then git checkout -q "$BRANCH"; else git checkout -q -b "$BRANCH" "origin/$BRANCH"; fi || { echo "checkout failed"; exit 1; }
  MINE="$CUR"                                      # your old branch gets merged in below
else
  MINE=""
fi

# 3. merge Claude's latest (and your old branch, if you were on another one)
conflict() {
  git merge --abort 2>/dev/null
  git push -q -f origin "$1:refs/heads/matt-local" && echo
  echo "CONFLICT: your changes overlap Claude's. Nothing was lost."
  echo "Your work is pushed to the branch 'matt-local'. Ask Claude to merge matt-local, then run this script again."
  exit 2
}
git merge -q --no-edit "origin/$BRANCH" || conflict HEAD
if [ -n "$MINE" ] && ! git merge-base --is-ancestor "$MINE" HEAD; then
  git merge -q --no-edit "$MINE" || conflict "$MINE"
fi

echo
git log --oneline -5
echo
if [ "$(git rev-list --count "origin/$BRANCH..HEAD")" -gt 0 ]; then
  echo "Up to date with Claude's branch; you also have local commits Claude doesn't have yet."
  echo "To send them: git push origin HEAD:refs/heads/matt-local   (then ask Claude to merge matt-local)"
else
  echo "Up to date with Claude's branch."
fi
echo "Restart the board server and refresh the browser."
