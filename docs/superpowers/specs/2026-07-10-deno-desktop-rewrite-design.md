# AWS Resource Explorer — Deno Desktop Rewrite

**Date:** 2026-07-10
**Status:** Approved design, pending implementation plan

## Goal

Replace the PySide6/Python desktop app with a Deno-based desktop app using
`@webview/webview` (webview_deno). Reach feature parity with the current app,
plus one enhancement: service facet filters. The Python code is removed from
the repo once parity is reached.

## Scope

**Parity features (from the current app):**

- AWS profile dropdown (from `~/.aws/config` + `~/.aws/credentials`)
- Region dropdown (static region list, same entries as today)
- Load button fetching all resources via the Resource Groups Tagging API
  with full pagination
- Real-time case-insensitive substring filter over ARNs
- Table clears when profile or region changes
- Status bar messages; controls disabled while loading
- Warning when no AWS profiles are configured

**Enhancements:**

- Service facet chips (parsed from ARNs, with counts, toggleable,
  AND-combined with the text filter)
- Live resource count during loading (replaces the indeterminate bar)
- Cancellable load (closing the SSE stream aborts pagination)

**Out of scope (first pass):**

- `deno compile` single-binary distribution (stretch goal; the webview
  native-library download at first run needs verification before committing
  to it)
- Tag columns/details, export, copy/open-in-console actions, multi-region
  loading, caching

## Architecture

One Deno process, two threads:

- **Main thread** (`main.ts`): spawns the server worker, waits for it to
  report its port via `postMessage`, opens a native window with
  `@webview/webview` pointed at `http://127.0.0.1:<port>`, then enters the
  blocking `webview.run()` loop. On window close it terminates the worker
  and exits.
- **Server worker** (`server/server.ts`, a Web Worker = real OS thread):
  runs `Deno.serve` bound to `127.0.0.1` on a random free port. Serves the
  static UI and the API, and owns all AWS SDK calls.

Rationale: `webview.run()` blocks its thread's event loop. Putting the HTTP
server and AWS work on a worker thread keeps pagination and SSE streaming
from being starved. It also allows server-only development
(`deno task serve`) with the UI open in a normal browser with devtools.

## Backend API

| Endpoint | Behavior |
|---|---|
| `GET /` and static files | Serves `ui/index.html`, `ui/app.js`, `ui/app.css` from disk |
| `GET /api/profiles` | Profile names parsed with `@smithy/shared-ini-file-loader` (same parser the AWS SDK uses, matching boto3's view). Empty list is a valid response. |
| `GET /api/regions` | Static region list (single source of truth, server-side in `server/regions.ts`) |
| `GET /api/resources?profile=X&region=Y` | Server-Sent Events stream (see below) |

**Resources SSE stream:** the handler creates a
`ResourceGroupsTaggingAPI` client with `fromIni({ profile })` and the given
region, then paginates `GetResources`. Events:

- `progress` — `{ count }` after each page (running total)
- `done` — `{ arns: string[] }` full list
- `error` — `{ message }` human-readable AWS error (expired SSO session,
  missing credentials, throttling, network failure)

Client closing the EventSource aborts the request, cancelling the load.

**Dependencies:** AWS SDK for JavaScript v3 and the ini loader via `npm:`
specifiers in `deno.json` imports. No bundler; no `node_modules` committed.

## Frontend UI

Vanilla HTML/CSS/JS — `ui/index.html`, `ui/app.css`, `ui/app.js`. No
framework, no build step.

- **Top bar:** profile dropdown, region dropdown, Load button. Changing
  either dropdown clears the table and filter. While loading, dropdowns
  disable and Load becomes Cancel (closes the EventSource).
- **Filter row:** text input (instant, case-insensitive, substring over
  ARN) plus facet chip row. Facets are derived client-side from loaded
  ARNs: service = third colon-delimited segment (`arn:aws:s3:...` → `s3`).
  Each chip shows a count, e.g. `s3 (14)`. Clicking toggles; multiple
  active chips OR together within the facet, and the facet set
  AND-combines with the text filter. Chips rebuild on each load.
- **Table:** single ARN column, click-to-sort, monospace font. All
  filtering is client-side over the in-memory list.
- **Status bar:** idle → "Select profile and region, then click Load";
  loading → live "Loading… N resources"; done →
  "Done! (N resources, M shown)" where M updates as filters change.

## Error handling

- No AWS profiles → inline warning banner with setup instructions.
- AWS/SSE `error` event → red status-bar message with the AWS error text.
- Server worker crash or port bind failure → main thread prints the error
  to stderr and exits non-zero (no dead window).

## Repo migration

New layout at repo root:

```
deno.json          # tasks (start, serve, test) + npm imports
main.ts            # webview bootstrap
server/
  server.ts        # Deno.serve, routing, static files, SSE
  aws.ts           # profile listing + tagging-API pagination
  regions.ts       # static region list
ui/
  index.html
  app.css
  app.js
```

- Work happens on a new `deno-rewrite` branch (this is a rewrite, not a UI
  tweak on `improve-ui`).
- Once parity is verified, delete: `window.py`, `form.ui`, `ui_form.py`,
  `resources_rc.py`, `resources.qrc`, `requirements.txt`,
  `aws-resource-explorer.pyproject`, `aws-resource-explorer.pyproject.user`,
  `aws-resource-explorer.spec`, `__pycache__/`. Keep `icon.png`/`icon.ico`.
- Rewrite the README for the Deno app (`deno task start`).
- Add `arw-*.yaml` and `arw.sh` to `.gitignore` — they contain live
  credentials and must never be committed.

## Testing

- `deno test` units for pure logic: ARN→service parsing, filter
  combination (text + chips), SSE event framing.
- API handler tests hitting `Deno.serve` in-process via `fetch`:
  profiles/regions endpoints; resources endpoint with a stubbed AWS client.
- Manual smoke test of the webview window on macOS (windowing is not
  unit-testable).
