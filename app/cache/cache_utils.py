import json
import hashlib

def make_cache_key(payload: dict) -> str:
    payload_str = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    return f"analysis:{payload_hash}"
