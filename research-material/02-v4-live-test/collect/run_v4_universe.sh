#!/bin/bash
# Detached launcher for V4UNIVERSE (per-pool reconstruction of the V4LIVE engine universe; see MANIFEST.md).
# Usage:
#   setsid nohup /home/user/dapparb/research-material/02-v4-live-test/collect/run_v4_universe.sh [extra args, e.g. --pin <block>] \
#     > /home/user/dapparb/research-material/02-v4-live-test/collect/run_v4_universe.log 2>&1 < /dev/null &
# Resumable: the script keeps checkpoints in collect/work/v4universe/ (enumeration, v4 load + static metadata, each sync
# batch); every attempt continues from the last checkpoint with the same pin/spec/flags. Up to 3 attempts.
# Heap capped at 1280 MB (V8 old space) to keep the process under ~1.5 GB RSS.
SENT=/home/user/dapparb/research-material/.sentinels
C=/home/user/dapparb/research-material/02-v4-live-test/collect
cd /home/user/dapparb/bot || exit 1
rm -f $SENT/V4UNIVERSE.DONE $SENT/V4UNIVERSE.FAILED
for attempt in 1 2 3; do
  echo "$(date -u +%FT%TZ) attempt $attempt start (launcher pid $$) args: $*"
  NODE_OPTIONS=--max-old-space-size=1280 LOG_JSON=1 npx tsx ../research-material/02-v4-live-test/collect/v4_universe_snapshot.ts "$@" >> $C/v4_universe_snapshot.log 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) attempt $attempt exit code $rc"
  [ -f $SENT/V4UNIVERSE.DONE ] && exit 0
  sleep 30
done
if [ ! -f $SENT/V4UNIVERSE.DONE ] && [ ! -f $SENT/V4UNIVERSE.FAILED ]; then
  printf "v4 universe snapshot exited with code %s after 3 attempts without writing a sentinel (see collect/v4_universe_snapshot.log)\n%s\n" "$rc" "$(date -u +%FT%TZ)" > $SENT/V4UNIVERSE.FAILED
fi
