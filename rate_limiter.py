import time
import threading


class TokenBucket:

    def __init__(self, capacity, refill_rate):

        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

        self.lock = threading.Lock()

    def allow_request(self):

        with self.lock:

            self._refill()

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            return False

    def _refill(self):

        now = time.time()

        time_passed = now - self.last_refill

        tokens_to_add = time_passed * self.refill_rate

        if tokens_to_add >= 1:

            self.tokens = min(
                self.capacity,
                self.tokens + tokens_to_add
            )

            self.last_refill = now


class RateLimiter:

    def __init__(self, capacity, refill_rate):

        self.capacity = capacity
        self.refill_rate = refill_rate

        # user_id -> TokenBucket
        self.user_buckets = {}

        self.lock = threading.Lock()

    def allow_request(self, user_id):

        with self.lock:

            if user_id not in self.user_buckets:

                self.user_buckets[user_id] = TokenBucket(
                    self.capacity,
                    self.refill_rate
                )

            bucket = self.user_buckets[user_id]

        return bucket.allow_request()

def main():

    limiter = RateLimiter(
        capacity=5,
        refill_rate=1
    )

    users = ["user1", "user2"]

    for _ in range(10):
        for user in users:
            if limiter.allow_request(user):
                print(f"{user}: request allowed")
            else:
                print(f"{user}: rate limited")
        time.sleep(0.5)

if __name__ == "__main__":
    main()