import { realDeps, startServer } from "./server.ts";

startServer(realDeps, (port) => {
  (self as unknown as { postMessage(msg: unknown): void }).postMessage({ port });
});
