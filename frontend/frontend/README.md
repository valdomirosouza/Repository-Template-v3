# frontend

**Language:** Node.js 20 / Next.js 14 | **Type:** Frontend | **Port:** 3000
**Owner:** frontend-team | **Spec:** `services.yaml`

Customer-facing UI and HITL operator approval interface. Calls the API Gateway at
`NEXT_PUBLIC_API_BASE_URL`.

## Quick start

```bash
# First time only — generate lock file:
cd frontend/frontend && pnpm install

# From the monorepo root:
make run-frontend APP=frontend      # Next.js dev server on :3000
make test-unit-frontend APP=frontend
make lint-frontend APP=frontend
```

## Environment variables

| Variable                   | Default                 | Description                                                    |
| -------------------------- | ----------------------- | -------------------------------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | API Gateway base URL                                           |
| `NEXT_PUBLIC_APP_ENV`      | `development`           | App environment label                                          |
| `NEXT_PUBLIC_HITL_MOCK`    | `0`                     | `1` = run the HITL console on in-memory mock data (no backend) |

## HITL operator console (`/hitl`)

The HITL approval queue is the reference operator console: it polls pending requests, shows each
proposed agent action with a **PII-masked preview** and a **risk band** (Low / Medium / High around
the 0.70 human-review threshold, CLAUDE.md LLM09), and submits approve/reject decisions with a
required rationale (`src/components/hitl/ApprovalCard.tsx`).

### Mock mode (demo / no backend)

Set `NEXT_PUBLIC_HITL_MOCK=1` to back the console with seeded, synthetic, PII-free data via
`src/lib/hitl/mockClient.ts` — no API Gateway and no operator JWT required. Useful for demos and for
the Playwright journey:

```bash
NEXT_PUBLIC_HITL_MOCK=1 pnpm dev        # console at http://localhost:3000/hitl (mock banner shown)
E2E_HITL_MOCK=1 pnpm e2e                # runs src/__tests__/e2e/hitl-approval.spec.ts against it
```

The live mode (`NEXT_PUBLIC_HITL_MOCK=0`, default) calls the real HITL API; the operator bearer token
is supplied via `Configuration.accessToken` (a deployment concern, not wired in this template). The
client selection lives in `src/lib/hitl/client.ts` (`getHitlClient` / `isMockMode`).

## Key pages

| Route       | Description                                |
| ----------- | ------------------------------------------ |
| `/`         | Home — navigation hub                      |
| `/hitl`     | HITL approval queue — operator approval UI |
| `/requests` | Request status tracking                    |

## API client

`src/lib/api/` contains typed wrappers over the API Gateway REST endpoints defined
in `docs/api/openapi/v1/openapi.yaml`. Regenerate after spec changes:

```bash
make gen-api-client-ts APP=frontend
```
