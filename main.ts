import { SizeHint, Webview } from "@webview/webview";

const worker = new Worker(
  new URL("./server/worker.ts", import.meta.url).href,
  { type: "module" },
);

let port: number;
try {
  port = await new Promise<number>((resolve, reject) => {
    worker.onmessage = (event) => resolve(event.data.port);
    worker.onerror = (event) => reject(new Error(event.message));
    setTimeout(() => reject(new Error("server did not start within 10s")), 10_000);
  });
} catch (error) {
  console.error(`Failed to start local server: ${error}`);
  worker.terminate();
  Deno.exit(1);
}

const webview = new Webview(false, {
  width: 1000,
  height: 700,
  hint: SizeHint.NONE,
});
webview.title = "AWS Resource Explorer";
webview.navigate(`http://127.0.0.1:${port}/`);
webview.run(); // blocks until the window is closed

worker.terminate();
Deno.exit(0);
