# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A desktop app for exploring AWS resources across profiles/regions, built with Deno 2.x and a native OS webview (`jsr:@webview/webview`). It fetches resources via the AWS Resource Groups Tagging API. Rewritten from PySide6/Python in July 2026 (`git log` before then refers to the old app; the release workflow in `.github/workflows/build-release.yml` still targets the Python app and is stale).

## Commands

```bash
deno task start          # run the desktop app (native window)
deno task serve          # server only — prints a URL; open in a browser for devtools
deno task test           # full test suite (= deno test -A)
deno test -A server/aws_test.ts                      # one test file
deno test -A --filter "loadResources yields" server/ # one test by name
```

There is no build/bundle step. All dependencies come from `deno.json` imports (JSR + npm specifiers); never add a package.json or commit node_modules. `deno.lock` is committed.

## Architecture

One Deno process, two threads:

- **Main thread** (`main.ts`): spawns the server worker, awaits a `{ port }` postMessage (10s timeout), opens the webview at `http://127.0.0.1:<port>/`, and blocks in `webview.run()` until the window closes. Needs `-A --unstable-ffi` (FFI for the webview dylib).
- **Server worker** (`server/worker.ts` → `server/server.ts`): `Deno.serve` bound to `127.0.0.1:0`. Serves `ui/` statically via `serveDir` and three endpoints: `GET /api/profiles`, `GET /api/regions`, and `GET /api/resources?profile=X&region=Y` (Server-Sent Events).

The worker split exists because `webview.run()` blocks its thread's event loop; the HTTP server and AWS pagination must live on a separate thread. `server/server.ts` also runs standalone (`import.meta.main`) for the `serve` task.

### SSE contract (server ↔ client)

`server/aws.ts:loadResources` is an async generator yielding `{type:"progress",count}` per page, then `{type:"done",arns}` or `{type:"error",message}`. `server/server.ts` frames each as an SSE event named after `type`; `ui/app.js` listens per event name. Two subtleties encoded in `app.js`: EventSource auto-reconnects after stream close (every terminal path must close the source or the load silently re-fires), and the `error` event fires for BOTH the custom SSE error and transport failures (distinguished by `event.data` presence). Client disconnect aborts pagination via `req.signal`, checked between pages.

### Testability seams

- `createHandler(deps: HandlerDeps)` takes `{ listProfiles, createClient }` — handler tests inject a stub `TaggingClient`, no AWS or network involved. `realDeps` is the production wiring.
- `ui/filter.js` is a pure ES module (no DOM) imported by both the browser (`ui/app.js`) and Deno tests. Keep filter/facet logic there, DOM wiring in `app.js`.
- `listProfiles` accepts optional file paths so tests use temp fixture files instead of the real `~/.aws`.

### Frontend

Vanilla HTML/CSS/JS in `ui/` (three files + filter.js), loaded directly by the webview — no framework, no build. All filtering/faceting is client-side over the in-memory ARN list. Element IDs in `index.html` are load-bearing for `app.js`.

## Constraints and gotchas

- The server must only ever bind `127.0.0.1`, and `createHandler` rejects non-local `Host` headers (403) as DNS-rebinding protection — don't loosen either.
- The `serve` task's explicit permission list is deliberate; the AWS SDK needs `--allow-sys` (osRelease for its user-agent), which was discovered the hard way. If a new SDK code path prompts for a permission, extend the task's flags, don't switch it to `-A`.
- `arw-*.yaml` and `arw.sh` in the repo root are the owner's local operational files containing live credentials. They are gitignored — never commit, read into artifacts, or "clean them up".
- `server/regions.ts` is a deliberately static 17-entry list in `"code (Name)"` format; the UI derives the API region code by splitting on the first space.
- Design docs live in `docs/superpowers/specs/` and `docs/superpowers/plans/` (the 2026-07-10 files document this rewrite's intended behavior).
