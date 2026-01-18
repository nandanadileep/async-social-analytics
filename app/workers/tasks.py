import time
import json

from app.workers.celery_app import celery_app
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key

BATCH_QUEUE_KEY = "analysis_batch_queue"
BATCH_SIZE = 5
CACHE_TTL_SECONDS = 3600


@celery_app.task
def process_batch():
    batch = []

    for _ in range(BATCH_SIZE):
        item = redis_client.lpop(BATCH_QUEUE_KEY)
        if not item:
            break
        batch.append(json.loads(item))

    if not batch:
        return "empty batch"

    print(f"Processing batch of size {len(batch)}")

    time.sleep(5)

    for entry in batch:
        payload = entry["payload"]
        result = {
            "status": "ok",
            "payload": payload,
        }

        cache_key = make_cache_key(payload)
        redis_client.setex(
            cache_key,
            CACHE_TTL_SECONDS,
            json.dumps(result),
        )

    return f"processed {len(batch)} items"
