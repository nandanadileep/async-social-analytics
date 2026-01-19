import time
import json

from app.workers.celery_app import celery_app
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key
from app.metrics.metrics import incr

BATCH_QUEUE_KEY = "analysis_batch_queue"


@celery_app.task
def process_batch():
    batch = []

    for _ in range(5):
        item = redis_client.lpop(BATCH_QUEUE_KEY)
        if not item:
            break
        batch.append(json.loads(item))

    if not batch:
        return "empty"

    incr("metrics:batches_processed")
    incr("metrics:batch_size_total", len(batch))

    time.sleep(5)

    for entry in batch:
        payload = entry["payload"]
        result = {"status": "ok", "payload": payload}
        redis_client.setex(
            make_cache_key(payload),
            3600,
            json.dumps(result),
        )

    return f"processed {len(batch)}"
