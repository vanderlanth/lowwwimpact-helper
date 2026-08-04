# Auth + Measure Pipeline (shared)

Single source of truth for **authenticating** against a site and **measuring** its pages
(initial/deferred KB weight + the 4 Lighthouse scores). Both the evaluate mode evaluator and the
evaluate debug flow (`evaluate --debug`) run this pipeline, so any fix made here applies to both.

The pipeline has two phases:

- **Phase A — Auth Setup**: detect a login, log in, and persist `workspace/auth-state.json`.
- **Phase B — Measure**: run `/measure-page-weight` (which auto-injects the saved auth state).

For a public site, Phase A is a no-op (no `auth-state.json` is written) and Phase B measures directly.

---

## Phase A — Auth Setup (login only)

This phase produces `workspace/auth-state.json` — the captured **login session** (cookies + per-origin
localStorage) for a site that sits behind a login. It is written **only when a login was performed**.

> **Cookie consent is handled separately, NOT here.** Consent is accepted **inline during the weight
> measurement** (a click in the measurement `run-code`), and is deliberately **not** persisted into
> `auth-state.json`. Reason: persisting "Accept all" would inject third-party **marketing** cookies
> (YouTube, LinkedIn, ad networks) into the Lighthouse run, which trips Lighthouse's
> `third-party-cookies` best-practices audit and tanks the score (observed best-practices 96 → 58).
> Keeping consent out of the saved state means weight reflects the real consented load (~40% heavier —
> e.g. 343 KB un-consented vs ~780 KB consented on a real marketing page) while Lighthouse still scores
> a clean first visit. See `commands/measure-page-weight.md` Step 2 (inline consent) and Step 3
> (Lighthouse injects only this login state, never consent).

For a public site with no login, Phase A is a no-op — no `auth-state.json` is written, and consent (if
any) is handled inline at measurement time.

**Step A1 — Open the site and detect a login redirect:**

```bash
playwright-cli -s=auth-login --browser=chromium open
playwright-cli -s=auth-login resize 1440 760
playwright-cli -s=auth-login goto <first non-login URL>
playwright-cli -s=auth-login run-code "async (page) => { await page.waitForTimeout(3000); return page.url(); }"
```

If the resulting URL contains `/login`, `/signin`, or `/auth` in the path or hash, the site requires
authentication — set `requires_auth = true`. If not, the site is public: skip the rest of Phase A and
do **not** write `auth-state.json`.

**Step A2 — Log in (only if `requires_auth`):**

1. Get credentials: look for a `.env` at `{workspace}/.env` or `{workspace}/../.env`, reading
   variables matching `*_USER` / `*_LOGIN` / `*_EMAIL` and `*_PASS` / `*_PASSWORD`. If none found,
   ask the user: *"This site requires a login. Please provide a username and password."*
2. Snapshot the login form, fill it, submit:

```bash
playwright-cli -s=auth-login goto <login URL>
playwright-cli -s=auth-login snapshot
playwright-cli -s=auth-login fill <username-field-ref> "<username>"
playwright-cli -s=auth-login fill <password-field-ref> "<password>"
playwright-cli -s=auth-login click <submit-button-ref>
playwright-cli -s=auth-login run-code "async (page) => { await page.waitForTimeout(3000); return page.url(); }"
```

If the URL still contains `/login`, `/signin`, or `/auth`, the credentials were rejected — stop and
report. Otherwise the login succeeded.

**Step A3 — Save the login state.** Use Playwright's native storage-state command, which captures
**both** cookies and per-origin localStorage in one step:

```bash
playwright-cli -s=auth-login state-save workspace/auth-state.json
playwright-cli -s=auth-login close
```

This writes the native Playwright `storageState` format:

```json
{
  "cookies": [{ "name": "...", "value": "...", "domain": "...", "path": "/", "httpOnly": true, "secure": true, "sameSite": "Lax", "expires": -1 }],
  "origins": [{ "origin": "https://example.com", "localStorage": [{ "name": "token", "value": "..." }] }]
}
```

> **Why `state-save` (not `run-code` + `fs`)**: the `run-code` sandbox does **not** expose Node's
> `require`, `fs`, or `process`. A `try { const fs = require('fs') … } catch {}` block silently
> swallows the `require is not defined` error and injects **no state**, so every downstream
> measurement lands on the login page or a banner-blocked page (null Lighthouse scores, garbage KB).
> `state-save` / `state-load` are first-class CLI commands that work entirely inside the browser
> process — they are the only reliable way to persist and restore the session here.

All subsequent steps load `workspace/auth-state.json` via `state-load` — no state is passed as a
parameter, and nothing reads the file from inside `run-code`. The filename stays `auth-state.json`
for backward compatibility even though it now also carries consent cookies.

---

## Phase B — Measure

Run the measurement engine for the target URL(s):

```
/measure-page-weight <url> [url2 url3 ...] [--out <path>]
```

`/measure-page-weight` (see `commands/measure-page-weight.md`) automatically loads
`workspace/auth-state.json` when it exists — via `state-load` into each Playwright
weight-measurement session, and via CDP cookie/localStorage injection into the Lighthouse Chrome
instance. It produces, per page: `initial_weight_kb`, `deferred_weight_kb`, and the four Lighthouse
scores. Callers set `--out` to control the output path (default `workspace/page-weights.json`).

---

## Auth-failure recovery

Lighthouse or the weight pass landing on the login page (instead of the authenticated page) means
the saved auth state was not accepted. Recover by:

1. Re-running **Phase A** — log in again and overwrite `workspace/auth-state.json`.
2. Re-running **Phase B** for the affected URL(s).

If it still fails, the failure is in one of three injection points, in order of likelihood: the login
form fill (Phase A), the `state-load` into the weight session, or the Lighthouse CDP auth injection.
The evaluate debug flow (`evaluate --debug`) exists to isolate which one.

**Hash-route SPAs** (auth gated by a token/timestamp in `localStorage`, e.g. URLs like
`https://site/en#/section`): `state-save`/`state-load` carry the localStorage origin across sessions,
so auth holds without any special handling. Confirm the deep link does not bounce to `#/login` by
checking `page.url()` after the measurement navigation.
