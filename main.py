"""
Task API — a small CRUD API for managing a to-do list.
Run: uvicorn main:app --reload --port 8000
Docs (Swagger UI): http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple in-memory CRUD API for managing tasks.",
)

# ---------- In-memory "database" ----------

tasks: List[dict] = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Read a book", "done": False},
    {"id": 3, "title": "Clean the house", "done": True},
]
next_id = 4  # tracks the next free id


# ---------- Request/response models ----------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------- Stage 1: root + health ----------

@app.get("/", summary="API info")
def root():
    """Basic info about this API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    """Simple liveness check."""
    return {"status": "ok"}


# ---------- Stage 2: Read ----------

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    """Returns the full list of tasks."""
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------- Stage 3: Create ----------

@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(new_task: TaskCreate):
    """Creates a new task. title must not be empty."""
    global next_id

    if not new_task.title or not new_task.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    task = {"id": next_id, "title": new_task.title.strip(), "done": False}
    tasks.append(task)
    next_id += 1
    return task


# ---------- Stage 4: Update & Delete ----------

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate):
    """Updates title and/or done for a task. 404 if id unknown, 400 if body invalid."""
    if update.title is None and update.done is None:
        raise HTTPException(status_code=400, detail="Provide at least title or done to update")

    if update.title is not None and not update.title.strip():
        raise HTTPException(status_code=400, detail="title cannot be empty")

    for task in tasks:
        if task["id"] == task_id:
            if update.title is not None:
                task["title"] = update.title.strip()
            if update.done is not None:
                task["done"] = update.done
            return task

    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Deletes a task by id. 404 if it doesn't exist."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------- Bonus: extras ----------

@app.get("/stats", summary="Task stats")
def get_stats():
    """Returns counts of total, done, and open tasks."""
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done, "open": total - done}


@app.post("/reset", summary="Reset tasks to seed data")
def reset_tasks():
    """Restores the original 3 example tasks. Useful for demos."""
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Read a book", "done": False},
        {"id": 3, "title": "Clean the house", "done": True},
    ]
    next_id = 4
    return {"message": "Tasks reset", "tasks": tasks}
