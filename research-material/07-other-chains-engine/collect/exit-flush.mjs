// Preload used only by this collector (not part of bot/src; loaded with `node --import tsx --import <this file>`).
// 1) scan.ts calls process.exit(0) right after out.end(), which drops JSONL rows still buffered in the write stream
//    (observed in the smoke test: the last scanned block had 87 rows in the log and 1 in the file). process.exit is
//    delayed by 5 s so the stream can flush.
// 2) On SIGTERM/SIGINT (sent by the collector's time-cap watchdog), the process keeps running for 5 s so queued
//    JSONL writes complete, then exits with 143/130. Without this, the default signal action kills the process
//    with writes still queued. No other behaviour is changed.
const realExit = process.exit.bind(process);
let exiting = false;
process.exit = (code) => {
  if (exiting) return;
  exiting = true;
  setTimeout(() => realExit(code), 5000);
};
for (const [sig, code] of [["SIGTERM", 143], ["SIGINT", 130]]) {
  process.on(sig, () => {
    if (exiting) return;
    exiting = true;
    process.stderr.write(`\n[exit-flush] ${sig} received at ${new Date().toISOString()}; flushing for 5 s then exiting ${code}\n`);
    setTimeout(() => realExit(code), 5000);
  });
}
