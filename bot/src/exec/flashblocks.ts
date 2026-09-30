import zlib from "node:zlib";
import { EventEmitter } from "node:events";
import { log } from "../util/log.js";

export interface Flashblock {
  blockNumber: bigint;
  index: number;
  txCount: number;
  /** raw signed transactions included in this flashblock */
  transactions: `0x${string}`[];
  receivedAt: number;
}

/**
 * Client for Base's Flashblocks websocket (brotli-compressed JSON, one message per ~200ms sub-block).
 * Emits "flashblock" for every message and "block" when index 0 of a new block arrives.
 */
export class FlashblocksClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private stopped = false;

  constructor(readonly url: string) {
    super();
  }

  start(): void {
    this.stopped = false;
    this.connect();
  }

  stop(): void {
    this.stopped = true;
    this.ws?.close();
  }

  private connect(): void {
    const ws = new WebSocket(this.url);
    this.ws = ws;
    ws.onopen = () => log.info({ url: this.url }, "flashblocks connected");
    ws.onmessage = async (m) => {
      try {
        const buf = Buffer.from(await (m.data as Blob).arrayBuffer());
        let txt: string;
        try {
          txt = zlib.brotliDecompressSync(buf).toString();
        } catch {
          txt = buf.toString();
        }
        const j = JSON.parse(txt);
        const fb: Flashblock = {
          blockNumber: BigInt(j.metadata?.block_number ?? 0),
          index: Number(j.index ?? 0),
          txCount: (j.diff?.transactions ?? []).length,
          transactions: j.diff?.transactions ?? [],
          receivedAt: Date.now(),
        };
        if (fb.index === 0) this.emit("block", fb);
        this.emit("flashblock", fb);
      } catch (e) {
        log.warn({ err: String(e).slice(0, 120) }, "flashblock decode failed");
      }
    };
    ws.onclose = () => {
      if (this.stopped) return;
      log.warn("flashblocks disconnected; reconnecting in 1s");
      setTimeout(() => this.connect(), 1000);
    };
    ws.onerror = (e) => log.warn({ err: String((e as any).message ?? e).slice(0, 120) }, "flashblocks ws error");
  }
}
