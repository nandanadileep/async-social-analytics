import time
import json
import uuid

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key
from app.workers.tasks import process_batch
from app.metrics.metrics import incr

app = FastAPI()

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

BATCH_QUEUE_KEY = "analysis_batch_queue"


@app.post("/analyze")
def analyze(payload: dict):
    start_time = time.time()

    cache_key = make_cache_key(payload)
    cached = redis_client.get(cache_key)

    if cached:
        incr("metrics:cache_hits")

        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "cached",
            "latency_ms": latency_ms,
            "result": json.loads(cached),
        }

    incr("metrics:cache_misses")

    request_id = str(uuid.uuid4())
    redis_client.rpush(
        BATCH_QUEUE_KEY,
        json.dumps({"request_id": request_id, "payload": payload}),
    )

    incr("metrics:tasks_enqueued")

    if redis_client.llen(BATCH_QUEUE_KEY) >= 5:
        process_batch.delay()

    latency_ms = int((time.time() - start_time) * 1000)
    return {
        "status": "queued",
        "request_id": request_id,
        "latency_ms": latency_ms,
    }

from app.metrics.metrics import get

@app.get("/metrics")
def metrics():
    return {
        "cache_hits": get("metrics:cache_hits"),
        "cache_misses": get("metrics:cache_misses"),
        "tasks_enqueued": get("metrics:tasks_enqueued"),
        "batches_processed": get("metrics:batches_processed"),
        "avg_batch_size": (
            get("metrics:batch_size_total") / max(get("metrics:batches_processed"), 1)
        ),
    }
