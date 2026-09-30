import pino from "pino";

export const log = pino({
  level: process.env.LOG_LEVEL ?? "info",
  transport: process.env.LOG_JSON ? undefined : { target: "pino-pretty", options: { colorize: true, translateTime: "HH:MM:ss.l" } },
});
