from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_task_returns_audit_event_and_next_action():
    response = client.post(
        "/v1/tasks",
        json={
            "title": "Review workspace copy",
            "owner_id": "usr_18",
            "state": "in_review",
            "requires_approval": True,
        },
    )
    payload = response.json()
    assert response.status_code == 201
    assert payload["task"]["state"] == "in_review"
    assert payload["audit_event"]["event_type"] == "task_created"
    assert payload["next_action"] == "approval_required"


def test_handoff_requires_reviewer_and_approval():
    created = client.post(
        "/v1/tasks",
        json={"title": "Prepare handoff", "owner_id": "usr_44", "requires_approval": True},
    ).json()["task"]
    task_id = created["id"]

    forbidden = client.patch(f"/v1/tasks/{task_id}", json={"state": "approved"})
    assert forbidden.status_code == 403

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


def test_invalid_title_is_rejected():
    response = client.post("/v1/tasks", json={"title": "   ", "owner_id": "usr_18"})
    assert response.status_code == 422
