#!/bin/bash
# Detached launcher for SHALLOW_SNAPSHOT. Usage: setsid nohup ./run_snapshot.sh [extra args, e.g. --pin <block>] > run_snapshot.log 2>&1 < /dev/null &
# The snapshot is a single pinned-block pass (~10-15 min). To redo it at the same block, pass --pin <pinned_block from snapshot-meta.json>.
SENT=/home/user/dapparb/research-material/.sentinels
cd /home/user/dapparb/bot || exit 1
rm -f $SENT/SHALLOW_SNAPSHOT.DONE $SENT/SHALLOW_SNAPSHOT.FAILED
LOG_JSON=1 npx tsx ../research-material/04-shallow-pools/collect/snapshot.ts "$@" > ../research-material/04-shallow-pools/collect/snapshot.log 2>&1
rc=$?
echo "$(date -u +%FT%TZ) snapshot exit code $rc"
if [ ! -f $SENT/SHALLOW_SNAPSHOT.DONE ] && [ ! -f $SENT/SHALLOW_SNAPSHOT.FAILED ]; then
  printf "snapshot process exited with code %s without writing a sentinel (see collect/snapshot.log)\n%s\n" "$rc" "$(date -u +%FT%TZ)" > $SENT/SHALLOW_SNAPSHOT.FAILED
fi
