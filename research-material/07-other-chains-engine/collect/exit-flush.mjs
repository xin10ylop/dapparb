// Preload used only by this collector (not part of bot/src). scan.ts calls process.exit(0) right after
// out.end(), which drops the JSONL rows still buffered in the write stream (observed in the smoke test:
// the last scanned block had 87 rows in the log and 1 in the file). This hook delays process.exit by 5 s
// so the stream can flush. It changes nothing else.
const realExit = process.exit.bind(process);
let exiting = false;
process.exit = (code) => {
  if (exiting) return;
  exiting = true;
  setTimeout(() => realExit(code), 5000);
};
