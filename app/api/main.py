import json
from fastapi import FastAPI
from app.workers.tasks import dummy_analysis_task
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key

app = FastAPI()

CACHE_TTL_SECONDS = 60 * 60 


@app.post("/analyze")
def analyze(payload: dict):
    cache_key = make_cache_key(payload)

    cached_result = redis_client.get(cache_key)
    if cached_result:
        return {
            "status": "cached",
            "result": json.loads(cached_result),
        }

    task = dummy_analysis_task.delay(payload)

    return {
        "status": "queued",
        "task_id": task.id,
        "cache_key": cache_key,
    }


@app.get("/result/{task_id}")
def get_result(task_id: str):
    task = dummy_analysis_task.AsyncResult(task_id)

    if task.successful():
        result = task.result
        return {
            "task_id": task_id,
            "state": task.state,
            "result": result,
        }

    return {
        "task_id": task_id,
        "state": task.state,
        "result": None,
    }
