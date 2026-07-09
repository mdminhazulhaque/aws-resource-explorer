# Deno Desktop Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the PySide6 desktop app with a Deno + webview desktop app (feature parity plus service facet filters), per `docs/superpowers/specs/2026-07-10-deno-desktop-rewrite-design.md`.

**Architecture:** One Deno process, two threads. The main thread opens a native window via `@webview/webview` pointed at a loopback HTTP server; that server runs in a Web Worker (`Deno.serve`), serves the static vanilla-JS UI, and exposes `/api/profiles`, `/api/regions`, and an SSE `/api/resources` stream that paginates the AWS Resource Groups Tagging API.

**Tech Stack:** Deno 2.x, `jsr:@webview/webview`, `jsr:@std/http` (serveDir), `jsr:@std/assert`, `npm:@aws-sdk/client-resource-groups-tagging-api`, `npm:@aws-sdk/credential-providers`, `npm:@smithy/shared-ini-file-loader`. Frontend: vanilla HTML/CSS/JS, no build step.

## Global Constraints

- Deno ≥ 2.0 required (`import.meta.dirname`, JSR imports).
- The HTTP server binds to `127.0.0.1` only, port 0 (OS-assigned).
- No frontend framework, no bundler, no `node_modules` committed; all dependencies come from `deno.json` imports.
- SSE event names are exactly `progress`, `done`, `error` with JSON payloads `{count}`, `{arns}`, `{message}`.
- The region list is copied verbatim from `window.py:16-34` (17 entries, `"code (Name)"` format).
- All work happens on the `deno-rewrite` branch created in Task 1.
- Run `deno test -A` after every task; all tests must pass before committing.

---

### Task 1: Branch, scaffold, and .gitignore

**Files:**
- Create: `deno.json`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `deno task start|serve|test` definitions and import aliases (`@webview/webview`, `@std/http`, `@std/assert`, `@aws-sdk/client-resource-groups-tagging-api`, `@aws-sdk/credential-providers`, `@smithy/shared-ini-file-loader`) used by every later task.

- [ ] **Step 1: Create the branch**

```bash
git checkout improve-ui && git checkout -b deno-rewrite
```

- [ ] **Step 2: Write `deno.json`**

```json
{
  "tasks": {
    "start": "deno run -A --unstable-ffi main.ts",
    "serve": "deno run --allow-net --allow-read --allow-env server/server.ts",
    "test": "deno test -A"
  },
  "imports": {
    "@webview/webview": "jsr:@webview/webview@^0.9",
    "@std/http": "jsr:@std/http@^1",
    "@std/assert": "jsr:@std/assert@^1",
    "@aws-sdk/client-resource-groups-tagging-api": "npm:@aws-sdk/client-resource-groups-tagging-api@^3",
    "@aws-sdk/credential-providers": "npm:@aws-sdk/credential-providers@^3",
    "@smithy/shared-ini-file-loader": "npm:@smithy/shared-ini-file-loader@^4"
  }
}
```

- [ ] **Step 3: Append to `.gitignore`**

Add these lines (the yaml/sh files contain live credentials and must never be committed):

```
# local operational files with credentials
arw-*.yaml
arw.sh
```

- [ ] **Step 4: Verify Deno and task registration**

Run: `deno --version` — Expected: `deno 2.x.x` (if missing or 1.x, install/upgrade via `curl -fsSL https://deno.land/install.sh | sh` and stop to inform the user).
Run: `deno task` — Expected: lists `start`, `serve`, `test`.
Run: `git status --short` — Expected: `arw-*.yaml`/`arw.sh` no longer appear as untracked.

- [ ] **Step 5: Commit**

```bash
git add deno.json .gitignore
git commit -m "chore: scaffold deno project, ignore credential-bearing local files"
```

---

### Task 2: Region list

**Files:**
- Create: `server/regions.ts`
- Test: `server/regions_test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `export const AWS_REGIONS: string[]` — 17 strings in `"code (Name)"` format, consumed by the `/api/regions` handler (Task 5).

- [ ] **Step 1: Write the failing test**

`server/regions_test.ts`:

```ts
import { assertEquals } from "@std/assert";
import { AWS_REGIONS } from "./regions.ts";

Deno.test("AWS_REGIONS has 17 entries in 'code (Name)' format", () => {
  assertEquals(AWS_REGIONS.length, 17);
  assertEquals(AWS_REGIONS[0], "us-east-1 (N. Virginia)");
  for (const region of AWS_REGIONS) {
    assertEquals(/^[a-z]{2}-[a-z]+-\d \(.+\)$/.test(region), true, region);
  }
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `deno test -A server/regions_test.ts`
Expected: FAIL — `Module not found "server/regions.ts"`.

- [ ] **Step 3: Write the implementation**

`server/regions.ts` (copied verbatim from `window.py`):

```ts
export const AWS_REGIONS = [
  "us-east-1 (N. Virginia)",
  "us-east-2 (Ohio)",
  "us-west-1 (N. California)",
  "us-west-2 (Oregon)",
  "ap-south-1 (Mumbai)",
  "ap-northeast-3 (Osaka)",
  "ap-northeast-2 (Seoul)",
  "ap-southeast-1 (Singapore)",
  "ap-southeast-2 (Sydney)",
  "ap-northeast-1 (Tokyo)",
  "ca-central-1 (Central)",
  "eu-central-1 (Frankfurt)",
  "eu-west-1 (Ireland)",
  "eu-west-2 (London)",
  "eu-west-3 (Paris)",
  "eu-north-1 (Stockholm)",
  "sa-east-1 (São Paulo)",
];
```

- [ ] **Step 4: Run test to verify it passes**

Run: `deno test -A server/regions_test.ts`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add server/regions.ts server/regions_test.ts
git commit -m "feat: add static AWS region list"
```

---

### Task 3: AWS profile listing

**Files:**
- Create: `server/aws.ts`
- Test: `server/aws_test.ts`

**Interfaces:**
- Consumes: `@smithy/shared-ini-file-loader`.
- Produces: `export async function listProfiles(paths?: ProfileFilePaths): Promise<string[]>` where `ProfileFilePaths = { configFilepath?: string; filepath?: string }` — sorted unique profile names. Task 5 calls it with no arguments.

- [ ] **Step 1: Write the failing test**

`server/aws_test.ts`:

```ts
import { assertEquals } from "@std/assert";
import { listProfiles } from "./aws.ts";

Deno.test("listProfiles merges and sorts config + credentials profiles", async () => {
  const dir = await Deno.makeTempDir();
  await Deno.writeTextFile(
    `${dir}/config`,
    "[profile alpha]\nregion = us-east-1\n\n[profile beta]\nregion = us-west-2\n",
  );
  await Deno.writeTextFile(
    `${dir}/credentials`,
    "[beta]\naws_access_key_id = x\n\n[gamma]\naws_access_key_id = y\n",
  );
  const profiles = await listProfiles({
    configFilepath: `${dir}/config`,
    filepath: `${dir}/credentials`,
  });
  assertEquals(profiles, ["alpha", "beta", "gamma"]);
});

Deno.test("listProfiles returns empty array when files are missing", async () => {
  const dir = await Deno.makeTempDir();
  const profiles = await listProfiles({
    configFilepath: `${dir}/none`,
    filepath: `${dir}/none2`,
  });
  assertEquals(profiles, []);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `deno test -A server/aws_test.ts`
Expected: FAIL — `Module not found "server/aws.ts"`.

- [ ] **Step 3: Write the implementation**

`server/aws.ts`:

```ts
import { loadSharedConfigFiles } from "@smithy/shared-ini-file-loader";

export interface ProfileFilePaths {
  configFilepath?: string;
  filepath?: string;
}

export async function listProfiles(
  paths: ProfileFilePaths = {},
): Promise<string[]> {
  const { configFile, credentialsFile } = await loadSharedConfigFiles({
    ...paths,
    ignoreCache: true,
  });
  const names = new Set([
    ...Object.keys(configFile),
    ...Object.keys(credentialsFile),
  ]);
  return [...names].sort();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `deno test -A server/aws_test.ts`
Expected: PASS (2 tests). First run will download the npm package; that's normal.

- [ ] **Step 5: Commit**

```bash
git add server/aws.ts server/aws_test.ts deno.lock
git commit -m "feat: list AWS profiles from shared config files"
```

---

### Task 4: Tagging API client and paginated load generator

**Files:**
- Modify: `server/aws.ts` (append)
- Test: `server/aws_test.ts` (append)

**Interfaces:**
- Consumes: nothing from earlier tasks (same file as Task 3).
- Produces (all from `server/aws.ts`, consumed by Task 5):
  - `export interface ResourcePage { arns: string[]; nextToken?: string }`
  - `export interface TaggingClient { getResources(paginationToken?: string): Promise<ResourcePage> }`
  - `export function createTaggingClient(profile: string, region: string): TaggingClient`
  - `export type LoadEvent = { type: "progress"; count: number } | { type: "done"; arns: string[] } | { type: "error"; message: string }`
  - `export async function* loadResources(client: TaggingClient): AsyncGenerator<LoadEvent>`

- [ ] **Step 1: Write the failing tests**

Append to `server/aws_test.ts`:

```ts
import { loadResources, type TaggingClient } from "./aws.ts";

function stubClient(pages: { arns: string[]; nextToken?: string }[]): TaggingClient {
  let call = 0;
  return { getResources: () => Promise.resolve(pages[call++]) };
}

Deno.test("loadResources yields progress per page then done with all ARNs", async () => {
  const client = stubClient([
    { arns: ["arn:aws:s3:::bucket-a"], nextToken: "t1" },
    { arns: ["arn:aws:lambda:us-east-1:123:function:fn"], nextToken: undefined },
  ]);
  const events = [];
  for await (const event of loadResources(client)) events.push(event);
  assertEquals(events, [
    { type: "progress", count: 1 },
    { type: "progress", count: 2 },
    {
      type: "done",
      arns: ["arn:aws:s3:::bucket-a", "arn:aws:lambda:us-east-1:123:function:fn"],
    },
  ]);
});

Deno.test("loadResources yields error event when the client throws", async () => {
  const client: TaggingClient = {
    getResources: () => Promise.reject(new Error("The SSO session has expired")),
  };
  const events = [];
  for await (const event of loadResources(client)) events.push(event);
  assertEquals(events, [{ type: "error", message: "The SSO session has expired" }]);
});
```

Note: `assertEquals` and `listProfiles` are already imported at the top of the file from Task 3; merge the `./aws.ts` imports into one statement.

- [ ] **Step 2: Run tests to verify they fail**

Run: `deno test -A server/aws_test.ts`
Expected: FAIL — `does not provide an export named 'loadResources'`.

- [ ] **Step 3: Write the implementation**

Append to `server/aws.ts`:

```ts
import {
  GetResourcesCommand,
  ResourceGroupsTaggingAPIClient,
} from "@aws-sdk/client-resource-groups-tagging-api";
import { fromIni } from "@aws-sdk/credential-providers";

export interface ResourcePage {
  arns: string[];
  nextToken?: string;
}

export interface TaggingClient {
  getResources(paginationToken?: string): Promise<ResourcePage>;
}

export function createTaggingClient(
  profile: string,
  region: string,
): TaggingClient {
  const client = new ResourceGroupsTaggingAPIClient({
    region,
    credentials: fromIni({ profile }),
  });
  return {
    async getResources(paginationToken) {
      const response = await client.send(
        new GetResourcesCommand(
          paginationToken ? { PaginationToken: paginationToken } : {},
        ),
      );
      return {
        arns: (response.ResourceTagMappingList ?? [])
          .map((resource) => resource.ResourceARN)
          .filter((arn): arn is string => Boolean(arn)),
        nextToken: response.PaginationToken || undefined,
      };
    },
  };
}

export type LoadEvent =
  | { type: "progress"; count: number }
  | { type: "done"; arns: string[] }
  | { type: "error"; message: string };

export async function* loadResources(
  client: TaggingClient,
): AsyncGenerator<LoadEvent> {
  const arns: string[] = [];
  let token: string | undefined;
  try {
    do {
      const page = await client.getResources(token);
      arns.push(...page.arns);
      token = page.nextToken;
      yield { type: "progress", count: arns.length };
    } while (token);
    yield { type: "done", arns };
  } catch (error) {
    yield {
      type: "error",
      message: error instanceof Error ? error.message : String(error),
    };
  }
}
```

(Move the new `import` statements to the top of the file with the existing one.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `deno test -A server/aws_test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add server/aws.ts server/aws_test.ts deno.lock
git commit -m "feat: paginated resource loading via tagging API"
```

---

### Task 5: HTTP server — routing, SSE, static files

**Files:**
- Create: `server/sse.ts`
- Create: `server/server.ts`
- Test: `server/server_test.ts`

**Interfaces:**
- Consumes: `AWS_REGIONS` (Task 2); `listProfiles`, `createTaggingClient`, `loadResources`, `TaggingClient` (Tasks 3–4).
- Produces (consumed by Tasks 7–8):
  - `server/sse.ts`: `export function sseMessage(event: string, data: unknown): string`
  - `server/server.ts`: `export interface HandlerDeps { listProfiles: () => Promise<string[]>; createClient: (profile: string, region: string) => TaggingClient }`
  - `export function createHandler(deps: HandlerDeps): (req: Request) => Promise<Response>`
  - `export function startServer(deps: HandlerDeps, onListen: (port: number) => void): Deno.HttpServer`
  - `export const realDeps: HandlerDeps`
  - Running `server/server.ts` directly (`deno task serve`) starts a dev server and prints its URL.

- [ ] **Step 1: Write the failing tests**

`server/server_test.ts`:

```ts
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `deno test -A server/server_test.ts`
Expected: FAIL — `Module not found "server/server.ts"`.

- [ ] **Step 3: Write the implementation**

`server/sse.ts`:

```ts
export function sseMessage(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
}
```

`server/server.ts`:

```ts
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `deno test -A server/`
Expected: PASS (9 tests across the three test files: 1 regions + 4 aws + 4 server).

- [ ] **Step 5: Commit**

```bash
git add server/sse.ts server/server.ts server/server_test.ts
git commit -m "feat: loopback HTTP server with SSE resource streaming"
```

---

### Task 6: Client-side filter logic

**Files:**
- Create: `ui/filter.js`
- Test: `ui/filter_test.js`

**Interfaces:**
- Consumes: nothing.
- Produces (plain ES module, imported by both `ui/app.js` in Task 7 and the Deno test):
  - `export function serviceOf(arn): string` — third colon-delimited ARN segment.
  - `export function facetCounts(arns): [string, number][]` — sorted by service name.
  - `export function applyFilters(arns, text, activeServices): string[]` — `activeServices` is a `Set`; empty set means no facet filtering; text match is case-insensitive substring; the two AND-combine.

- [ ] **Step 1: Write the failing test**

`ui/filter_test.js`:

```js
import { assertEquals } from "@std/assert";
import { applyFilters, facetCounts, serviceOf } from "./filter.js";

const ARNS = [
  "arn:aws:s3:::my-bucket",
  "arn:aws:s3:::other-bucket",
  "arn:aws:lambda:us-east-1:123:function:handler",
];

Deno.test("serviceOf extracts the service segment", () => {
  assertEquals(serviceOf("arn:aws:s3:::my-bucket"), "s3");
  assertEquals(serviceOf("not-an-arn"), "");
});

Deno.test("facetCounts counts per service, sorted by name", () => {
  assertEquals(facetCounts(ARNS), [["lambda", 1], ["s3", 2]]);
});

Deno.test("applyFilters: empty text and no facets returns everything", () => {
  assertEquals(applyFilters(ARNS, "", new Set()), ARNS);
});

Deno.test("applyFilters: text is case-insensitive substring", () => {
  assertEquals(applyFilters(ARNS, "MY-BUCKET", new Set()), ["arn:aws:s3:::my-bucket"]);
});

Deno.test("applyFilters: facets OR together and AND with text", () => {
  assertEquals(applyFilters(ARNS, "", new Set(["s3"])).length, 2);
  assertEquals(applyFilters(ARNS, "other", new Set(["s3"])), ["arn:aws:s3:::other-bucket"]);
  assertEquals(applyFilters(ARNS, "", new Set(["s3", "lambda"])).length, 3);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `deno test -A ui/filter_test.js`
Expected: FAIL — `Module not found "ui/filter.js"`.

- [ ] **Step 3: Write the implementation**

`ui/filter.js`:

```js
export function serviceOf(arn) {
  return arn.split(":")[2] ?? "";
}

export function facetCounts(arns) {
  const counts = new Map();
  for (const arn of arns) {
    const service = serviceOf(arn);
    counts.set(service, (counts.get(service) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

export function applyFilters(arns, text, activeServices) {
  const query = text.trim().toLowerCase();
  return arns.filter((arn) =>
    (!query || arn.toLowerCase().includes(query)) &&
    (activeServices.size === 0 || activeServices.has(serviceOf(arn)))
  );
}
```

Note: `serviceOf("not-an-arn")` — `"not-an-arn".split(":")` is `["not-an-arn"]`, so index 2 is `undefined` → `""`. The `?? ""` handles it.

- [ ] **Step 4: Run test to verify it passes**

Run: `deno test -A ui/filter_test.js`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add ui/filter.js ui/filter_test.js
git commit -m "feat: client-side ARN filter and facet logic"
```

---

### Task 7: Frontend UI

**Files:**
- Create: `ui/index.html`
- Create: `ui/app.css`
- Create: `ui/app.js`
- Test: `server/server_test.ts` (append one static-file test)

**Interfaces:**
- Consumes: `applyFilters`, `facetCounts` from `ui/filter.js` (Task 6); the three API endpoints (Task 5).
- Produces: the complete UI served at `/`. Element IDs used by `app.js`: `profile`, `region`, `load`, `filter`, `facets`, `tbody`, `status`, `banner`, `arn-header`.

- [ ] **Step 1: Write the failing static-file test**

Append to `server/server_test.ts`:

```ts
Deno.test("GET / serves the UI index page", async () => {
  const handler = createHandler(stubDeps([]));
  const resp = await handler(new Request("http://localhost/"));
  assertEquals(resp.status, 200);
  assert((await resp.text()).includes("AWS Resource Explorer"));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `deno test -A server/server_test.ts`
Expected: FAIL — status is 404 (no `ui/index.html` yet).

- [ ] **Step 3: Write `ui/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AWS Resource Explorer</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <header>
    <div id="banner" hidden>
      No AWS profiles found. Please configure <code>~/.aws/credentials</code>
      or <code>~/.aws/config</code> before using this application.
    </div>
    <div class="controls">
      <label>Profile <select id="profile"></select></label>
      <label>Region <select id="region"></select></label>
      <button id="load">Load</button>
    </div>
    <div class="filter-row">
      <input id="filter" type="search" placeholder="Filter by ARN substring…" autocomplete="off">
      <div id="facets"></div>
    </div>
  </header>
  <main>
    <table>
      <thead><tr><th id="arn-header" title="Click to sort">Resource ARN</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </main>
  <footer id="status">Loading UI…</footer>
  <script type="module" src="/app.js"></script>
</body>
</html>
```

- [ ] **Step 4: Write `ui/app.css`**

```css
* { box-sizing: border-box; margin: 0; }

html, body { height: 100%; }

body {
  display: flex;
  flex-direction: column;
  font: 14px/1.4 -apple-system, "Segoe UI", system-ui, sans-serif;
  color: #1c2733;
  background: #f5f6f8;
}

header {
  padding: 12px 16px 8px;
  background: #fff;
  border-bottom: 1px solid #dde1e6;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

#banner {
  padding: 8px 12px;
  border-radius: 6px;
  background: #fff3cd;
  border: 1px solid #e0c76a;
}

.controls { display: flex; gap: 12px; align-items: center; }
.controls label { display: flex; gap: 6px; align-items: center; }

select, input, button {
  font: inherit;
  padding: 5px 8px;
  border: 1px solid #c3c9d0;
  border-radius: 6px;
  background: #fff;
}

button {
  background: #1a73e8;
  color: #fff;
  border-color: #1a73e8;
  cursor: pointer;
  padding: 5px 16px;
}
button:hover { background: #1765cc; }

.filter-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
#filter { flex: 0 0 280px; }

#facets { display: flex; gap: 6px; flex-wrap: wrap; }
.chip {
  background: #eef1f4;
  color: #1c2733;
  border: 1px solid #c3c9d0;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 12px;
}
.chip:hover { background: #e2e7ec; }
.chip.active {
  background: #1a73e8;
  color: #fff;
  border-color: #1a73e8;
}

main { flex: 1; overflow: auto; }

table { width: 100%; border-collapse: collapse; background: #fff; }
th {
  position: sticky;
  top: 0;
  text-align: left;
  padding: 6px 16px;
  background: #eef1f4;
  border-bottom: 1px solid #dde1e6;
  cursor: pointer;
  user-select: none;
}
td {
  padding: 3px 16px;
  border-bottom: 1px solid #f0f2f4;
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  font-size: 12px;
  white-space: nowrap;
}
tr:hover td { background: #f5f9ff; }

footer {
  padding: 6px 16px;
  background: #fff;
  border-top: 1px solid #dde1e6;
  color: #5a6572;
}
footer.error { color: #c5221f; font-weight: 600; }

select:disabled { opacity: 0.5; }
```

- [ ] **Step 5: Write `ui/app.js`**

```js
import { applyFilters, facetCounts } from "./filter.js";

const els = {
  profile: document.getElementById("profile"),
  region: document.getElementById("region"),
  load: document.getElementById("load"),
  filter: document.getElementById("filter"),
  facets: document.getElementById("facets"),
  tbody: document.getElementById("tbody"),
  status: document.getElementById("status"),
  banner: document.getElementById("banner"),
  arnHeader: document.getElementById("arn-header"),
};

const state = {
  arns: [],
  activeServices: new Set(),
  source: null, // EventSource while a load is in flight
  sortAsc: null, // null = API order, true/false = sorted
};

function setStatus(text, isError = false) {
  els.status.textContent = text;
  els.status.classList.toggle("error", isError);
}

function setLoading(loading) {
  els.profile.disabled = loading;
  els.region.disabled = loading;
  els.load.textContent = loading ? "Cancel" : "Load";
}

function render() {
  const shown = applyFilters(state.arns, els.filter.value, state.activeServices);
  if (state.sortAsc !== null) {
    shown.sort((a, b) => state.sortAsc ? a.localeCompare(b) : b.localeCompare(a));
  }
  els.tbody.replaceChildren(...shown.map((arn) => {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.textContent = arn;
    tr.append(td);
    return tr;
  }));
  if (state.arns.length > 0) {
    setStatus(`Done! (${state.arns.length} resources, ${shown.length} shown)`);
  }
}

function renderFacets() {
  els.facets.replaceChildren(...facetCounts(state.arns).map(([service, count]) => {
    const chip = document.createElement("button");
    chip.className = "chip" + (state.activeServices.has(service) ? " active" : "");
    chip.textContent = `${service} (${count})`;
    chip.onclick = () => {
      if (state.activeServices.has(service)) {
        state.activeServices.delete(service);
      } else {
        state.activeServices.add(service);
      }
      renderFacets();
      render();
    };
    return chip;
  }));
}

function cancelLoad() {
  if (state.source) {
    state.source.close();
    state.source = null;
  }
  setLoading(false);
}

function clearTable() {
  cancelLoad();
  state.arns = [];
  state.activeServices.clear();
  state.sortAsc = null;
  els.filter.value = "";
  renderFacets();
  els.tbody.replaceChildren();
  setStatus("Select profile and region, then click Load");
}

function startLoad() {
  clearTable();
  setLoading(true);
  setStatus("Loading …");
  const params = new URLSearchParams({
    profile: els.profile.value,
    region: els.region.value.split(" ")[0],
  });
  const source = new EventSource(`/api/resources?${params}`);
  state.source = source;

  source.addEventListener("progress", (event) => {
    setStatus(`Loading … ${JSON.parse(event.data).count} resources`);
  });

  source.addEventListener("done", (event) => {
    state.arns = JSON.parse(event.data).arns;
    cancelLoad();
    renderFacets();
    render();
  });

  // Fires for BOTH our custom `event: error` SSE messages (which carry
  // .data) and transport-level failures (which don't) — hence the check.
  source.addEventListener("error", (event) => {
    if (!state.source) return; // already handled by done/cancel
    const message = event.data
      ? JSON.parse(event.data).message
      : "Connection to local server lost";
    cancelLoad();
    setStatus(`Error: ${message}`, true);
  });
}

async function init() {
  const [profiles, regions] = await Promise.all([
    fetch("/api/profiles").then((r) => r.json()),
    fetch("/api/regions").then((r) => r.json()),
  ]);
  if (profiles.length === 0) els.banner.hidden = false;
  els.profile.append(...profiles.map((p) => new Option(p, p)));
  els.region.append(...regions.map((r) => new Option(r, r)));
  setStatus("Select profile and region, then click Load");
}

els.load.onclick = () => {
  if (state.source) {
    cancelLoad();
    setStatus("Load cancelled");
  } else {
    startLoad();
  }
};
els.filter.oninput = render;
els.profile.onchange = clearTable;
els.region.onchange = clearTable;
els.arnHeader.onclick = () => {
  state.sortAsc = state.sortAsc === null ? true : !state.sortAsc;
  render();
};

init();
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `deno test -A`
Expected: PASS (15 tests total: 9 server-side + 1 static-file + 5 filter).

- [ ] **Step 7: Manual browser verification**

Run: `deno task serve` — Expected output: `Dev server: http://127.0.0.1:<port>/`.
Open that URL in a browser and verify:
1. Profile and region dropdowns are populated (profiles from your real `~/.aws`).
2. Click Load with a valid profile → status shows live counts → table fills with ARNs, facet chips appear with counts.
3. Type in the filter box → rows narrow instantly; click a chip → it highlights and combines with the text filter; status shows "N resources, M shown".
4. Click the column header → rows sort ascending, click again → descending.
5. Change profile or region → table, chips, and filter clear.
6. Click Load, then Cancel mid-load → status shows "Load cancelled".
7. Load with a profile whose SSO session is expired (if available) → red error message in the status bar.

Stop the server with Ctrl+C when done. If any check fails, fix before committing.

- [ ] **Step 8: Commit**

```bash
git add ui/index.html ui/app.css ui/app.js server/server_test.ts
git commit -m "feat: vanilla JS UI with facet chips, live progress, and cancel"
```

---

### Task 8: Webview bootstrap

**Files:**
- Create: `main.ts`
- Create: `server/worker.ts`

**Interfaces:**
- Consumes: `startServer`, `realDeps` from `server/server.ts` (Task 5).
- Produces: `deno task start` opens the native desktop window. `server/worker.ts` posts `{ port: number }` to the main thread once listening.

- [ ] **Step 1: Write `server/worker.ts`**

```ts
import { realDeps, startServer } from "./server.ts";

startServer(realDeps, (port) => {
  (self as unknown as { postMessage(msg: unknown): void }).postMessage({ port });
});
```

- [ ] **Step 2: Write `main.ts`**

```ts
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
```

- [ ] **Step 3: Type-check**

Run: `deno check main.ts server/worker.ts`
Expected: no errors. First run downloads `@webview/webview` from JSR.

- [ ] **Step 4: Manual smoke test (macOS)**

Run: `deno task start`
Expected: a native 1000×700 window titled "AWS Resource Explorer" opens showing the UI (first run downloads the webview native library). Repeat manual checks 1–3 from Task 7 Step 7 inside the window. Close the window — the process must exit cleanly (check with `echo $?` → `0`).

If the webview library fails to load, note the exact error and stop for review rather than working around it silently.

- [ ] **Step 5: Commit**

```bash
git add main.ts server/worker.ts deno.lock
git commit -m "feat: native desktop window via webview_deno"
```

---

### Task 9: Remove the Python app and rewrite the README

**Files:**
- Delete: `window.py`, `form.ui`, `ui_form.py`, `resources_rc.py`, `resources.qrc`, `requirements.txt`, `aws-resource-explorer.pyproject`, `aws-resource-explorer.pyproject.user`, `aws-resource-explorer.spec`, `__pycache__/`
- Modify: `README.md` (full rewrite)

**Interfaces:**
- Consumes: a fully working app (Tasks 1–8 complete, all manual checks passed).
- Produces: a Python-free repo whose README documents the Deno app.

- [ ] **Step 1: Confirm parity before deleting**

All Task 7 Step 7 and Task 8 Step 4 manual checks must have passed. If not, stop — do not delete the Python app.

- [ ] **Step 2: Delete the Python app**

```bash
git rm window.py form.ui ui_form.py resources_rc.py resources.qrc \
  requirements.txt aws-resource-explorer.pyproject \
  aws-resource-explorer.pyproject.user aws-resource-explorer.spec
rm -rf __pycache__
```

- [ ] **Step 3: Rewrite `README.md`**

Replace the entire file with:

````markdown
# AWS Resource Explorer

A lightweight desktop app for exploring AWS resources across profiles and
regions, built with [Deno](https://deno.com) and a native OS webview.
Resources are fetched with the AWS Resource Groups Tagging API and filtered
instantly in the UI.

![AWS Resource Explorer](.media/screenshot-win.png)

## Features

- **Multi-profile** — pick any profile from `~/.aws/config` / `~/.aws/credentials`
- **Multi-region** — explore any AWS region
- **Full pagination** — loads *all* resources, with a live running count
- **Instant filtering** — case-insensitive substring search over ARNs
- **Service facets** — one-click chips (`s3`, `lambda`, …) with counts,
  combinable with the text filter
- **Cancellable loads** — stop a long fetch mid-flight
- **Native window** — a single Deno process, no Electron

## Requirements

- [Deno](https://docs.deno.com/runtime/getting_started/installation/) 2.0+
- AWS credentials configured (`aws configure` or SSO)

## Run

```bash
git clone https://github.com/mdminhazulhaque/aws-resource-explorer.git
cd aws-resource-explorer
deno task start
```

The first run downloads dependencies and the webview native library.

## Development

```bash
deno task serve   # server only — open the printed URL in a browser
deno task test    # run the test suite
```

## Usage

1. Select an AWS **profile** and **region**
2. Click **Load** — all resources are fetched with live progress
3. Narrow results with the **filter box** and/or **service chips**
4. Click the column header to sort; click **Cancel** to stop a load

## License

MIT — see [LICENSE](LICENSE).
````

- [ ] **Step 4: Verify nothing references the deleted files**

Run: `grep -rn "ui_form\|window\.py\|pyside" --include="*.md" --include="*.ts" --include="*.js" --include="*.json" . | grep -v docs/superpowers`
Expected: no output.
Run: `deno test -A`
Expected: all 15 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat!: replace PySide6 app with Deno webview app"
```
