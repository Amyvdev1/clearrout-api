# ClearRoute API

**Personal portfolio demonstration** of a small workflow API with explicit states, a visible role boundary, and audit-friendly events.

ClearRoute is intentionally narrow. It models a common operations problem: a task needs an owner, a state, an approval rule, and a clear next action. The project is designed to make those parts inspectable from an interface or another service.

## What this demo includes

- `POST /v1/tasks` to create a task with an owner, state, and approval flag.
- `PATCH /v1/tasks/{task_id}` to move a task through a controlled state flow.
- A role-aware demonstration gate via `X-Demo-Role`.
- Audit events generated for task creation and state changes.
- Validation for empty titles and invalid task states.
- A test suite covering creation, review authority, handoff rules, and validation.

## Intentional boundaries

This is **not production software**. It uses an in-memory store and a request-header role demonstration rather than persistent storage, real authentication, or a deployed identity provider. It has no customer data, client integrations, or external execution. Those omissions are deliberate so the project stays small, safe, and easy to review.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Run tests

```bash
pytest -q
```

## Example

```bash
curl -X POST http://127.0.0.1:8000/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Review workspace copy","owner_id":"usr_18","state":"in_review","requires_approval":true}'
```

## Portfolio context

Built as a self-directed code sample by **Amy Villa**. The companion visual walkthrough is available in the technical portfolio under **ClearRoute API**.
