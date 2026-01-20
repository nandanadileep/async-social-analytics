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

        # Try to fetch real data
        try:
            import asyncio
            import os
            from app.adapters.factory import get_adapter
            
            # Prioritize SocialData.tools if key is present (cheaper/unofficial)
            if os.getenv("SOCIALDATA_API_KEY"):
                adapter = get_adapter('socialdata')
                platform_name = "SocialData"
            else:
                adapter = get_adapter('twitter')
                platform_name = "Twitter (Official)"
            
            # Fetch posts asynchronously
            social_posts = asyncio.run(adapter.fetch_posts(topic, max_results=120))
            
            # Extract text from SocialPost objects
            posts = [post.text for post in social_posts]
            
            if not posts:
                raise Exception("No posts returned from adapter")

            print(f"✅ Fetched {len(posts)} posts from {platform_name} adapter for topic: {topic}")
        except Exception as e:
            # Fallback to mock data if adapter fails
            print(f"⚠️ Adapter ({platform_name if 'platform_name' in locals() else 'Unknown'}) failed: {e}")
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
    """
    Generate mock posts for testing.
    
    In production, this is replaced by the adapter system.
    Use fetch_posts_from_adapter() for real data.
    """
    return [
        f"{topic} is amazing for developers #{i}"
        if i % 3 == 0
        else f"I am unsure about {topic} future #{i}"
        if i % 3 == 1
        else f"{topic} is overhyped and risky #{i}"
        for i in range(count)
    ]


async def fetch_posts_from_adapter(topic: str, count: int = 100, platform: str = "twitter"):
    """
    Fetch real posts using the adapter system.
    
    Args:
        topic: Topic/hashtag to search for
        count: Number of posts to fetch
        platform: Social media platform ('twitter', 'reddit', etc.)
        
    Returns:
        List of post texts
        
    Example:
        To switch to real Twitter data, replace generate_mock_posts() 
        with this function in process_batch().
    """
    from app.adapters.factory import get_adapter
    
    # Create adapter instance
    adapter = get_adapter(platform)
    
    # Fetch posts
    posts = await adapter.fetch_posts(topic, max_results=count)
    
    # Extract text from posts
    return [post.text for post in posts]
