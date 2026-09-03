# ClearRoute API — Code Tour

ClearRoute keeps the core workflow rules in one small FastAPI module so an engineer can trace a task from validation to a state update and audit record.

## 1. API setup

`app/main.py` creates the FastAPI application and gives it a versioned portfolio-demo description. FastAPI generates the OpenAPI schema and interactive `/docs` page from the typed models and route declarations.

## 2. Domain model and validation

`TaskState` limits a task to four allowed states: `planned`, `in_review`, `approved`, and `handed_off`. `TaskCreate` validates task titles and owners, defaults a new task to `planned`, and strips title whitespace before rejecting empty values. `TaskPatch`, `Task`, and `TaskWithAudit` keep the accepted update shape and returned records explicit.

## 3. Demo storage and audit schema

`TASKS` and `AUDIT_EVENTS` are module-level containers used only for this compact demonstration. `AuditEvent` captures the event type, task ID, detail, acting role, and UTC timestamp. The code makes the nonpersistent storage choice visible rather than hiding it behind a production-like name.

## 4. Role boundary

The `demo_role` dependency reads `X-Demo-Role`, allows `builder` or `reviewer`, and returns a 403 response for another value. The code and README call this a demonstration gate. It is deliberately not presented as authentication or authorization infrastructure.

## 5. Events and next actions

`create_event` creates an `evt_` identifier, timestamps the record, and appends it to the demo audit collection. `next_action` derives a specific workflow instruction from task state and approval rules. Keeping that mapping in one function makes the behavior predictable for a frontend client.

## 6. Routes and controlled transitions

The create route persists a task in the in-memory store, emits `task_created`, and returns a 201 response. The patch route returns 404 for an unknown ID, requires the reviewer role for approval/handoff, rejects an approval-required handoff before approval with 409, updates the task timestamp, and emits `state_changed`. The audit route retrieves only events for a known task.

## 7. Tests and packaging

`tests/test_main.py` uses FastAPI’s TestClient to validate creation output, reviewer-only transitions, approval-before-handoff, and invalid-title rejection. `requirements.txt` pins the direct dependencies. `pyproject.toml` configures the local test path, while the Dockerfile provides a small Python 3.12 runtime command.

## What the code sample proves—and what it does not

The repository is evidence of a typed FastAPI API design, validation, deterministic transition rules, audit-event behavior, tests, and container configuration. It is not evidence of database durability, concurrency handling, real user authentication, client integration, production deployment, scale, observability, or security certification.
