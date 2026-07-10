import { assert, assertEquals } from "@std/assert";
import { createHandler, type HandlerDeps } from "./server.ts";
import type { TaggingClient } from "./aws.ts";

function stubDeps(pages: { arns: string[]; nextToken?: string }[]): HandlerDeps {
  let call = 0;
  const client: TaggingClient = {
    getResources: () => Promise.resolve(pages[call++]),
  };
  return {
    listProfiles: () => Promise.resolve(["work", "personal"]),
    createClient: () => client,
  };
}

Deno.test("GET /api/profiles returns the profile list as JSON", async () => {
  const handler = createHandler(stubDeps([]));
  const resp = await handler(new Request("http://localhost/api/profiles"));
  assertEquals(resp.status, 200);
  assertEquals(await resp.json(), ["work", "personal"]);
});

Deno.test("GET /api/regions returns 17 regions", async () => {
  const handler = createHandler(stubDeps([]));
  const resp = await handler(new Request("http://localhost/api/regions"));
  assertEquals((await resp.json()).length, 17);
});

Deno.test("GET /api/resources without params returns 400", async () => {
  const handler = createHandler(stubDeps([]));
  const resp = await handler(new Request("http://localhost/api/resources"));
  assertEquals(resp.status, 400);
  await resp.body?.cancel();
});

Deno.test("GET /api/resources streams SSE progress and done events", async () => {
  const handler = createHandler(stubDeps([
    { arns: ["arn:aws:s3:::a"], nextToken: "t" },
    { arns: ["arn:aws:sqs:us-east-1:123:q"], nextToken: undefined },
  ]));
  const resp = await handler(
    new Request("http://localhost/api/resources?profile=work&region=us-east-1"),
  );
  assertEquals(resp.headers.get("content-type"), "text/event-stream");
  const text = await resp.text();
  assert(text.includes('event: progress\ndata: {"type":"progress","count":1}\n\n'));
  assert(text.includes('event: progress\ndata: {"type":"progress","count":2}\n\n'));
  assert(text.includes("event: done\n"));
  assert(text.includes("arn:aws:sqs:us-east-1:123:q"));
});
