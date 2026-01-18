from fastapi import FastAPI
import json
import uuid

from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key
from app.workers.tasks import process_batch

app = FastAPI()

BATCH_QUEUE_KEY = "analysis_batch_queue"


@app.post("/analyze")
def analyze(payload: dict):
    cache_key = make_cache_key(payload)

    cached = redis_client.get(cache_key)
    if cached:
        return {
            "status": "cached",
            "result": json.loads(cached),
        }

    request_id = str(uuid.uuid4())
    item = {
        "request_id": request_id,
        "payload": payload,
    }

    redis_client.rpush(BATCH_QUEUE_KEY, json.dumps(item))

    queue_length = redis_client.llen(BATCH_QUEUE_KEY)
    if queue_length >= 5:
        process_batch.delay()

    return {
        "status": "queued_for_batch",
        "request_id": request_id,
    }
