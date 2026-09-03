# ClearRoute API

> **A focused FastAPI workflow API demonstration with explicit task state, role-aware approval gates, and audit-friendly events.**

[Portfolio walkthrough](https://amy-villa-signal-gallery.vercel.app/projects/clearrout-api) · [Amy Villa on GitHub](https://github.com/Amyvdev1) · [Contact Amy](mailto:amyv.dev@gmail.com)

ClearRoute models a small but common systems problem: a task needs a clear owner, an explicit state, an approval requirement, an audit trail, and a predictable next action. The project is intentionally narrow so its API contract and transition rules are easy to inspect.

## What Amy built

| Capability | Implementation |
|---|---|
| **Task contract** | Pydantic request and response models define title, owner, state, approval requirement, timestamps, and audit data. |
| **Controlled workflow state** | `planned`, `in_review`, `approved`, and `handed_off` are constrained through an enum and transition logic. |
| **Visible role boundary** | An `X-Demo-Role` dependency models `builder` and `reviewer` behavior; approval and handoff require the reviewer role. |
| **Audit events** | Task creation and state changes create timestamped event records connected to the task. |
| **Next action** | A single function turns the current task state into `move_to_review`, `approval_required`, `handoff_ready`, or `complete`. |
| **Executable checks** | The test suite covers creation, review authority, approval-before-handoff, and whitespace-only title rejection. |
| **Local packaging** | Pinned requirements, Pytest configuration, and a Python 3.12 Dockerfile document a reproducible local run path. |

## API surface

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/health` | Returns a small health response for the portfolio API. |
| `POST` | `/v1/tasks` | Validates and creates a task, then records a creation event. |
| `GET` | `/v1/tasks` | Returns the tasks held by the in-memory demo store. |
| `PATCH` | `/v1/tasks/{task_id}` | Applies a controlled state update, enforcing role and approval rules. |
| `GET` | `/v1/tasks/{task_id}/audit` | Returns audit records associated with a known task. |

## Code map

| File / area | What it explains |
|---|---|
| [`app/main.py`](app/main.py) | FastAPI initialization, models, state constraints, demo role dependency, next-action logic, endpoint behavior, and audit-event creation. |
| [`tests/test_main.py`](tests/test_main.py) | Behavioral checks for the API’s creation, permission, transition, and validation rules. |
| [`requirements.txt`](requirements.txt) | Pinned FastAPI, Uvicorn, pytest, and HTTPX dependencies. |
| [`pyproject.toml`](pyproject.toml) | Pytest import/test-path configuration. |
| [`Dockerfile`](Dockerfile) | A compact Python 3.12 runtime image that starts Uvicorn on port 8000. |

For a behavior-level explanation of each source area, read the [technical code tour](docs/CODE_TOUR.md).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to inspect FastAPI’s generated API documentation.

## Run tests

```bash
pytest -q
```

The reviewed local suite contains **three tests** that passed during the project build. Their purpose is to protect the four core behaviors above, not to claim production completeness.

## Intentional boundaries

ClearRoute is a **self-directed code sample**, not production software. It uses module-level in-memory storage and a request-header demonstration role rather than a database, real authentication, identity-provider integration, customer data, external execution, monitoring, or deployment infrastructure. The explicit scope makes the transition logic and API design easy to inspect.

---

Created by **Amy Villa** as a focused backend/API portfolio project.
