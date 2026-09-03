# ClearRoute — API Consumer Guide

ClearRoute is a **personal FastAPI workflow code sample**. It gives a frontend or integration consumer a deliberately small, inspectable contract for creating a task, progressing it through controlled states, and reading local audit events. The project is useful for discussing validation, predictable failure modes, workflow rules, and the boundary between a demonstration role gate and real authorization.

## Core API contract

| Endpoint | Consumer purpose | Key rules |
|---|---|---|
| `GET /health` | Confirms the local demo API responds. | Returns a compact health response. |
| `POST /v1/tasks` | Creates a task with a title, owner, and approval requirement. | New tasks always start in `planned`; invalid initial states are rejected. |
| `GET /v1/tasks` | Lists local demo tasks. | Uses the demonstration role header. |
| `PATCH /v1/tasks/{task_id}` | Requests one controlled state transition. | The requested next state must be a legal edge in the graph. |
| `GET /v1/tasks/{task_id}/audit` | Reads the recorded local task events. | Returns `404` for an unknown task. |

## Create a task

```bash
curl -s \
  -X POST http://127.0.0.1:8000/v1/tasks \
  -H 'Content-Type: application/json' \
  -H 'X-Demo-Role: builder' \
  -d '{
    "title": "Review integration handoff",
    "owner_id": "usr_18",
    "requires_approval": true
  }'
```

The response includes the typed task, a `task_created` event, and the next action (`move_to_review`). This makes a useful integration decision visible immediately rather than asking the client to infer it.

## Follow the legal state graph

```text
planned → in_review → approved → handed_off
                 └────────────→ handed_off  (only when approval is not required)
```

A reviewer advances an approval-required task:

```bash
curl -s \
  -X PATCH http://127.0.0.1:8000/v1/tasks/<task_id> \
  -H 'Content-Type: application/json' \
  -H 'X-Demo-Role: reviewer' \
  -d '{"state":"approved"}'
```

## Consumer-facing error behavior

| Situation | Response | Consumer interpretation |
|---|---|---|
| Unknown task | `404 Task not found.` | Refresh the local task list or show a resource-not-found state. |
| Skipped, repeated, or reverse transition | `409 Conflict` with the allowed next state | Keep the UI aligned to the state graph; do not retry the same invalid transition. |
| Handoff before required approval | `409 Approved state is required before handoff.` | Direct the work back to review/approval. |
| Builder attempts approval or handoff | `403 Reviewer role is required…` | Request an appropriate reviewer action. |
| Empty title or non-`planned` creation | `422` validation response | Show the API validation message and preserve the user’s correctable input. |

The focused tests in [`tests/test_main.py`](../tests/test_main.py) exercise these branches. They are intentionally scoped behavioral tests, not production-load or security tests.

## Role-header boundary

`X-Demo-Role` accepts `builder` and `reviewer` to make role-dependent behavior easy to reproduce locally. It is **not authentication, authorization, identity proof, or an identity-provider integration**. A production integration would replace it with verified user/session context and add real authorization policy, tenant boundaries, durable audit storage, and reviewable access controls.

## What an integration conversation can cover

This sample supports an honest technical conversation about:

- translating business approval rules into a constrained API state graph;
- returning useful `404`, `403`, `409`, and `422` outcomes rather than silently accepting an invalid workflow action;
- keeping an audit event associated with the resulting task change; and
- identifying the concrete work needed before connecting an API to SSO, SCIM, SAML, OAuth/OIDC, a directory, or a customer environment.

Those identity and enterprise integrations are intentionally **not implemented** in ClearRoute. The distinction is important: the repository evidences API and workflow foundations, not production IAM, customer deployment, or enterprise security claims.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to inspect FastAPI’s generated API documentation.
