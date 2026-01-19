from app.cache.redis_client import redis_client

def incr(key: str, amount: int = 1):
    redis_client.incrby(key, amount)

def get(key: str) -> int:
    val = redis_client.get(key)
    return int(val) if val else 0
