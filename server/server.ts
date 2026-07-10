import { serveDir } from "@std/http";
import { AWS_REGIONS } from "./regions.ts";
import {
  createTaggingClient,
  listProfiles,
  loadResources,
  type TaggingClient,
} from "./aws.ts";
import { sseMessage } from "./sse.ts";

export interface HandlerDeps {
  listProfiles: () => Promise<string[]>;
  createClient: (profile: string, region: string) => TaggingClient;
}

const uiRoot = `${import.meta.dirname}/../ui`;

export function createHandler(deps: HandlerDeps) {
  return async (req: Request): Promise<Response> => {
    const url = new URL(req.url);
    if (url.pathname === "/api/profiles") {
      return Response.json(await deps.listProfiles());
    }
    if (url.pathname === "/api/regions") {
      return Response.json(AWS_REGIONS);
    }
    if (url.pathname === "/api/resources") {
      const profile = url.searchParams.get("profile");
      const region = url.searchParams.get("region");
      if (!profile || !region) {
        return Response.json(
          { message: "profile and region are required" },
          { status: 400 },
        );
      }
      return sseResponse(deps.createClient(profile, region), req.signal);
    }
    return serveDir(req, { fsRoot: uiRoot, quiet: true });
  };
}

function sseResponse(client: TaggingClient, signal: AbortSignal): Response {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        for await (const event of loadResources(client)) {
          if (signal.aborted) break;
          controller.enqueue(encoder.encode(sseMessage(event.type, event)));
        }
        controller.close();
      } catch {
        // client disconnected mid-stream; nothing to clean up
      }
    },
  });
  return new Response(body, {
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-cache",
    },
  });
}

export const realDeps: HandlerDeps = {
  listProfiles: () => listProfiles(),
  createClient: createTaggingClient,
};

export function startServer(
  deps: HandlerDeps,
  onListen: (port: number) => void,
): Deno.HttpServer {
  return Deno.serve(
    {
      hostname: "127.0.0.1",
      port: 0,
      onListen: ({ port }) => onListen(port),
    },
    createHandler(deps),
  );
}

if (import.meta.main) {
  startServer(realDeps, (port) =>
    console.log(`Dev server: http://127.0.0.1:${port}/`));
}
