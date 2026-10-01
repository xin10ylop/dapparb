#!/usr/bin/env bash
# Records the state of the public repository named as "Source Code" in arXiv 2606.00720v2 (Wu & Oz):
# remote refs, the commit, and the file tree (path, blob sha, size). No file content is written here;
# file contents are fetched by fetch_sources.py (slugs github-m1kuw1ll-base-arbitrage-competition-*), pinned to the commit.
# api.github.com answered HTTP 403 in this container, so plain git over HTTPS is used.
# Usage: ./list_repo_wu_oz.sh > list_repo_wu_oz.log 2>&1
set -euo pipefail
REPO=https://github.com/M1kuW1ll/base_arbitrage_competition
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo "run_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "repository: $REPO"
echo "== git ls-remote $REPO"
git ls-remote "$REPO"
echo "== shallow clone (--depth 1 --filter=blob:none --no-checkout), git log -1"
git clone -q --depth 1 --filter=blob:none --no-checkout "$REPO" "$TMP/repo"
git -C "$TMP/repo" log -1 --format='commit %H%nauthor %an%nauthor_date %aI%ncommitter %cn%ncommit_date %cI%nsubject %s'
echo "== git ls-tree -r -l HEAD (mode type blob_sha size path)"
git -C "$TMP/repo" ls-tree -r -l HEAD
echo "== files named README* (case-insensitive) at HEAD"
git -C "$TMP/repo" ls-tree -r --name-only HEAD | grep -i '^readme' || echo "(none)"
echo "done_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
