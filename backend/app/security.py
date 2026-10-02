
import os
import time
from collections import defaultdict, deque

WINDOW = 60
LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
buckets = defaultdict(deque)

def allow(client_key: str) -> bool:
    now = time.time()
    bucket = buckets[client_key]
    while bucket and now - bucket[0] > WINDOW:
        bucket.popleft()
    if len(bucket) >= LIMIT:
        return False
    bucket.append(now)
    return True
