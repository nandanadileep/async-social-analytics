import json
import time

from app.workers.celery_app import celery_app
from app.cache.redis_client import redis_client
from app.cache.cache_utils import make_cache_key
from app.analytics.sentiment import analyze_sentiments
from app.analytics.words import extract_word_frequencies
from app.metrics.metrics import incr

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

    incr("metrics:batches_processed")
    incr("metrics:batch_size_total", len(batch))

    for entry in batch:
        payload = entry["payload"]
        topic = payload["topic"]

        posts = generate_mock_posts(topic, count=120)

        sentiment = analyze_sentiments(posts)
        word_freq = extract_word_frequencies(posts)

        result = {
            "topic": topic,
            "total_posts": len(posts),
            "sentiment": sentiment,
            "top_words": word_freq,
        }

        redis_client.setex(
            make_cache_key(payload),
            CACHE_TTL_SECONDS,
            json.dumps(result),
        )

    return f"processed batch of {len(batch)}"


def generate_mock_posts(topic, count=100):
    return [
        f"{topic} is amazing for developers #{i}"
        if i % 3 == 0
        else f"I am unsure about {topic} future #{i}"
        if i % 3 == 1
        else f"{topic} is overhyped and risky #{i}"
        for i in range(count)
    ]
