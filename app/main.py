"""ClearRoute API — a small, self-contained workflow API portfolio demo.

This project intentionally uses an in-memory store and a demonstration role header.
It is designed to make validation, task states and audit events easy to inspect;
it is not production authentication or persistent storage.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="ClearRoute API",
    version="0.2.0",
    description=(
        "A portfolio demonstration of a role-aware workflow API with clear states "
        "and audit-friendly events. Uses in-memory demo data only."
    ),
)


class TaskState(str, Enum):
    planned = "planned"
    in_review = "in_review"
    approved = "approved"
    handed_off = "handed_off"


ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.planned: {TaskState.in_review},
    TaskState.in_review: {TaskState.approved, TaskState.handed_off},
    TaskState.approved: {TaskState.handed_off},
    TaskState.handed_off: set(),
}


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=140, examples=["Review workspace copy"])
    owner_id: str = Field(min_length=3, max_length=64, examples=["usr_18"])
    state: TaskState = TaskState.planned
    requires_approval: bool = True

    @field_validator("title")
    @classmethod
    def title_must_contain_content(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title must contain visible characters")
        return cleaned


class TaskPatch(BaseModel):
    state: TaskState


class Task(BaseModel):
    id: str
    title: str
    owner_id: str
    state: TaskState
    requires_approval: bool
    created_at: datetime
    updated_at: datetime


class AuditEvent(BaseModel):
    id: str
    task_id: str
    event_type: Literal["task_created", "state_changed"]
    detail: str
    actor_role: str
    occurred_at: datetime


class TaskWithAudit(BaseModel):
    task: Task
    audit_event: AuditEvent
    next_action: str


TASKS: dict[str, Task] = {}
AUDIT_EVENTS: list[AuditEvent] = []


def now() -> datetime:
    return datetime.now(timezone.utc)


def demo_role(x_demo_role: str = Header(default="builder")) -> str:
    """A visible demo gate, not authentication.

    Production systems should use a real identity provider and database-backed
    authorization. The header lets the portfolio demo show a clear role boundary.
    """
    if x_demo_role not in {"builder", "reviewer"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo role must be builder or reviewer.",
        )
    return x_demo_role


def create_event(task_id: str, event_type: Literal["task_created", "state_changed"], detail: str, actor_role: str) -> AuditEvent:
    event = AuditEvent(
        id=f"evt_{uuid4().hex[:8]}",
        task_id=task_id,
        event_type=event_type,
        detail=detail,
        actor_role=actor_role,
        occurred_at=now(),
    )
    AUDIT_EVENTS.append(event)
    return event


def next_action(task: Task) -> str:
    if task.requires_approval and task.state == TaskState.in_review:
        return "approval_required"
    if not task.requires_approval and task.state == TaskState.in_review:
        return "handoff_ready"
    if task.state == TaskState.approved:
        return "handoff_ready"
    if task.state == TaskState.handed_off:
        return "complete"
    return "move_to_review"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "portfolio-demo"}


@app.post("/v1/tasks", response_model=TaskWithAudit, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, role: str = Depends(demo_role)) -> TaskWithAudit:
    if payload.state != TaskState.planned:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="New tasks must begin in planned state.")
    timestamp = now()
    task = Task(
        id=f"tsk_{uuid4().hex[:8]}",
        title=payload.title,
        owner_id=payload.owner_id,
        state=payload.state,
        requires_approval=payload.requires_approval,
        created_at=timestamp,
        updated_at=timestamp,
    )
    TASKS[task.id] = task
    event = create_event(task.id, "task_created", "Task created with an explicit owner and state.", role)
    return TaskWithAudit(task=task, audit_event=event, next_action=next_action(task))


@app.get("/v1/tasks", response_model=list[Task])
def list_tasks(role: str = Depends(demo_role)) -> list[Task]:
    return list(TASKS.values())


@app.patch("/v1/tasks/{task_id}", response_model=TaskWithAudit)
def update_task_state(task_id: str, payload: TaskPatch, role: str = Depends(demo_role)) -> TaskWithAudit:
    task = TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    if payload.state not in ALLOWED_TRANSITIONS[task.state]:
        allowed = ", ".join(state.value for state in ALLOWED_TRANSITIONS[task.state]) or "none"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transition from {task.state.value} to {payload.state.value} is not allowed. Allowed next state: {allowed}.",
        )
    if task.requires_approval and payload.state == TaskState.handed_off and task.state != TaskState.approved:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approved state is required before handoff.")
    if role != "reviewer" and payload.state in {TaskState.approved, TaskState.handed_off}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reviewer role is required for approval or handoff.")
    previous_state = task.state
    task.state = payload.state
    task.updated_at = now()
    event = create_event(task.id, "state_changed", f"State changed from {previous_state.value} to {task.state.value}.", role)
    return TaskWithAudit(task=task, audit_event=event, next_action=next_action(task))


@app.get("/v1/tasks/{task_id}/audit", response_model=list[AuditEvent])
def task_audit(task_id: str, role: str = Depends(demo_role)) -> list[AuditEvent]:
    if task_id not in TASKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return [event for event in AUDIT_EVENTS if event.task_id == task_id]
