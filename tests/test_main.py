import pytest
from fastapi.testclient import TestClient

from app.main import AUDIT_EVENTS, TASKS, app


@pytest.fixture(autouse=True)
def reset_demo_store():
    TASKS.clear()
    AUDIT_EVENTS.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_task(client: TestClient, *, requires_approval: bool = True) -> dict:
    response = client.post(
        "/v1/tasks",
        json={
            "title": "Review workspace copy",
            "owner_id": "usr_18",
            "requires_approval": requires_approval,
        },
    )
    assert response.status_code == 201
    return response.json()["task"]


def test_new_task_starts_planned_with_a_visible_next_action(client: TestClient):
    task = create_task(client)
    assert task["state"] == "planned"

    listed = client.get("/v1/tasks")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == task["id"]


def test_explicit_approval_workflow_allows_only_legal_edges(client: TestClient):
    task = create_task(client, requires_approval=True)
    task_id = task["id"]

    review = client.patch(f"/v1/tasks/{task_id}", json={"state": "in_review"})
    assert review.status_code == 200
    assert review.json()["next_action"] == "approval_required"

    approved = client.patch(
        f"/v1/tasks/{task_id}",
        headers={"X-Demo-Role": "reviewer"},
        json={"state": "approved"},
    )
    assert approved.status_code == 200
    assert approved.json()["next_action"] == "handoff_ready"

    handed_off = client.patch(
        f"/v1/tasks/{task_id}",
        headers={"X-Demo-Role": "reviewer"},
        json={"state": "handed_off"},
    )
    assert handed_off.status_code == 200
    assert handed_off.json()["next_action"] == "complete"


def test_rejects_skipped_reverse_and_repeated_transitions(client: TestClient):
    task = create_task(client)
    task_id = task["id"]

    skipped = client.patch(
        f"/v1/tasks/{task_id}",
        headers={"X-Demo-Role": "reviewer"},
        json={"state": "approved"},
    )
    assert skipped.status_code == 409
    assert "not allowed" in skipped.json()["detail"]

    client.patch(f"/v1/tasks/{task_id}", json={"state": "in_review"})
    repeated = client.patch(f"/v1/tasks/{task_id}", json={"state": "in_review"})
    assert repeated.status_code == 409

    client.patch(
        f"/v1/tasks/{task_id}",
        headers={"X-Demo-Role": "reviewer"},
        json={"state": "approved"},
    )
    reverse = client.patch(f"/v1/tasks/{task_id}", json={"state": "in_review"})
    assert reverse.status_code == 409


def test_handoff_needs_reviewer_and_approval_when_required(client: TestClient):
    task = create_task(client)
    task_id = task["id"]
    client.patch(f"/v1/tasks/{task_id}", json={"state": "in_review"})

    premature = client.patch(
        f"/v1/tasks/{task_id}",
        headers={"X-Demo-Role": "reviewer"},
        json={"state": "handed_off"},
    )
    assert premature.status_code == 409
    assert "Approved state" in premature.json()["detail"]

    blocked = client.patch(f"/v1/tasks/{task_id}", json={"state": "approved"})
    assert blocked.status_code == 403


def test_invalid_title_and_nonplanned_creation_are_rejected(client: TestClient):
    invalid_title = client.post("/v1/tasks", json={"title": "   ", "owner_id": "usr_18"})
    assert invalid_title.status_code == 422

    invalid_initial_state = client.post(
        "/v1/tasks",
        json={"title": "Skip planning", "owner_id": "usr_18", "state": "in_review"},
    )
    assert invalid_initial_state.status_code == 422
    assert "planned state" in invalid_initial_state.json()["detail"]
