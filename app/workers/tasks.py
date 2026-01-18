import time
import json

from app.workers.celery_app import celery_app
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key

CACHE_TTL_SECONDS = 60 * 60


@celery_app.task(bind=True)
def dummy_analysis_task(self, payload):
    time.sleep(5)

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

    return result