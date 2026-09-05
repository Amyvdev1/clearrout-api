# ClearRoute API

> **API design + explicit workflow state with typed validation, transition rules, role boundaries, and audit events.**

[Source](https://github.com/Amyvdev1/clearrout-api) · [Amy Villa on GitHub](https://github.com/Amyvdev1) · [Contact](mailto:amyv.dev@gmail.com)

## What it solves

ClearRoute models a small but common backend problem: a task needs a clear owner, an explicit state, an approval rule, a predictable next action, and an audit trail that an API consumer can reason about.

## Why it exists

Workflow APIs become difficult to integrate when state changes are implicit or errors are inconsistent. ClearRoute keeps the state graph deliberately small so the contract is easy to inspect: legal transitions are explicit, role-gated actions are visible, invalid moves fail predictably, and every accepted change creates an audit event.

## Live demo

**Production deployment: pending.** The API is fully inspectable locally through FastAPI's generated `/docs` interface and the automated test suite. No external credentials or services are required.

## Architecture

```text
API consumer / FastAPI docs
          │
          ▼
FastAPI route layer
  ├── Pydantic request validation
  ├── demo role dependency
  ├── task-state transition rules
  └── predictable HTTP error contracts
          │
          ▼
In-memory demo store
  ├── tasks
  └── audit events
```

### Stack

**Python · FastAPI · Pydantic · REST · pytest · HTTPX · Docker · GitHub Actions**

## Key engineering decisions

| Decision | Why it is here |
|---|---|
| **Explicit transition graph** | Makes legal and illegal state changes visible instead of scattering transition logic across endpoints. |
| **Typed Pydantic contracts** | Gives API consumers predictable request/response validation behavior. |
| **`409 Conflict` for invalid transitions** | Distinguishes a valid request shape from a request that conflicts with current resource state. |
| **Visible demo role boundary** | Demonstrates role-sensitive behavior without pretending a request header is production authentication. |
| **Audit event creation** | Preserves a reviewable record of task creation and accepted state changes. |
| **Single next-action function** | Converts backend state into a simple consumer-facing next step. |
| **In-memory persistence boundary** | Keeps the sample focused on API/state semantics and explicitly avoids claiming durable production storage. |

## State-transition contract

| Current state | Allowed next state | Role / rule |
|---|---|---|
| `planned` | `in_review` | Builder or reviewer demo role. |
| `in_review` | `approved` | Reviewer demo role required. |
| `in_review` | `handed_off` | Reviewer demo role, only when `requires_approval` is `false`. |
| `approved` | `handed_off` | Reviewer demo role required. |
| `handed_off` | None | Terminal demo state. |

## Failure behavior

The API is designed so integration failures are distinguishable:

- invalid request data → `422 Unprocessable Entity`,
- missing task → `404 Not Found`,
- insufficient demo role → `403 Forbidden`,
- skipped/repeated/reverse transition → `409 Conflict`,
- handoff before required approval → `409 Conflict`.

The `X-Demo-Role` header is a teaching boundary, **not authentication**. It exists to make role-dependent behavior easy to inspect and test.

## API surface

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/health` | Returns a small health response. |
| `POST` | `/v1/tasks` | Validates and creates a task, then records a creation event. |
| `GET` | `/v1/tasks` | Returns tasks held by the demo store. |
| `PATCH` | `/v1/tasks/{task_id}` | Applies a controlled state update, enforcing role and approval rules. |
| `GET` | `/v1/tasks/{task_id}/audit` | Returns audit records associated with a known task. |

## Testing & CI

```bash
pytest -q
```

The regression suite covers initial state, legal transitions, skipped/repeated/reverse-state rejection, approval-before-handoff, reviewer authority, missing resources, and invalid task creation. GitHub Actions runs the focused API suite on pushes and pull requests.

## Security / evidence boundaries

ClearRoute is a **self-directed API engineering sample**, not production software. It uses module-level in-memory storage and a request-header demonstration role rather than a database, real authentication, identity-provider integration, durable audit controls, customer data, external execution, monitoring, or production deployment infrastructure.

The scope is intentionally narrow so the API contract and workflow invariants remain easy to review.

## 5-minute code review path

1. [`app/main.py`](app/main.py) — Pydantic models, transition graph, role dependency, next-action logic, endpoints, and audit events.
2. [`tests/test_main.py`](tests/test_main.py) — legal/illegal transitions, permissions, validation, and failure contracts.
3. [`docs/API_CONSUMER_GUIDE.md`](docs/API_CONSUMER_GUIDE.md) — consumer-oriented request/response examples and integration boundaries.
4. [`docs/CODE_TOUR.md`](docs/CODE_TOUR.md) — behavior-level source walkthrough.
5. [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — automated regression path.
6. [`Dockerfile`](Dockerfile) — compact Python 3.12 runtime packaging.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the generated API documentation.

---

Built by **Amy Villa** as an inspectable API Design & Workflow State engineering sample.
