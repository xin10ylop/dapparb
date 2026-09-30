#!/bin/bash
# Writes the code state used by a run: git HEAD, uncommitted changes under bot/src (other agents edit bot/src
# concurrently), and sha256 of every bot/src file. Usage: provenance.sh <out_file>
R=/home/user/dapparb
{
  echo "captured_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "git_head: $(git -C $R rev-parse HEAD)"
  echo "git_status_bot_src (uncommitted changes present in the working tree when the run started):"
  git -C $R status --short bot/src
  echo "git_diff_stat_bot_src:"
  git -C $R diff --stat bot/src
  echo "sha256 of bot/src/**/*.ts:"
  (cd $R && find bot/src -name '*.ts' -type f | sort | xargs sha256sum)
  echo "node: $(node --version); viem: $(node -p "require('$R/bot/node_modules/viem/package.json').version"); tsx: $(node -p "require('$R/bot/node_modules/tsx/package.json').version")"
} > "$1"
