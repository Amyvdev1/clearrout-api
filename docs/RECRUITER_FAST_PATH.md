# Recruiter Fast Path — ClearRoute API

ClearRoute is a compact **personal FastAPI code sample** for reviewing API foundations. It is designed to make validation, task state, a demonstration role boundary, audit events, and deterministic next actions easy to inspect.

## What to inspect first

1. [`app/main.py`](../app/main.py) for Pydantic models, the `TaskState` enum, controlled transitions, the `X-Demo-Role` demonstration gate, audit-event creation, and versioned routes.
2. [`tests/test_main.py`](../tests/test_main.py) for focused behavior checks covering task creation/audit output, reviewer-only transitions, approval-before-handoff, and invalid title rejection.
3. [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) for the automated pytest verification path on pushes and pull requests.
4. [`docs/CODE_TOUR.md`](CODE_TOUR.md) for a source-level explanation of design choices and the intentional scope boundary.

## Run and verify

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore FastAPI-generated API documentation.

## Good interview questions

- How are invalid task states and approval requirements handled?
- Why does the project use `X-Demo-Role`, and why is it not production authorization?
- How would the in-memory dictionaries become durable, concurrent persistence?
- What would be needed for real identity, RBAC, tenant isolation, audit durability, idempotency, logs/metrics/traces, and deployment?

## Explicit boundary

The source demonstrates a typed API contract, deterministic workflow logic, validation, focused tests, and local container packaging. It is **not** a production service and does not claim database durability, authentication, client data, deployment, monitoring, scale, or security certification.
