from fastapi import FastAPI
from app.workers.tasks import dummy_analysis_task

app = FastAPI()

@app.post("/analyze")
def analyze(payload: dict):
    task = dummy_analysis_task.delay(payload)
    return {
        "task_id": task.id,
        "status": "queued",
    }

@app.get("/result/{task_id}")
def get_result(task_id: str):
    task = dummy_analysis_task.AsyncResult(task_id)

    return {
    "task_id": task_id,
    "state": task.state,
    "result": task.result,
    "error": str(task.result) if task.failed() else None,
}

