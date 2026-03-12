from collections import defaultdict, deque
import time

class RateLimiter:
    def __init__(self, max_limit, window_size):
        self.max_limit = max_limit
        self.window_size = window_size
        self.requests = defaultdict(deque)
    
    def allow_requests(self, user):
        current_time = time.time()
        user_request = self.requests[user]

        while user_request and current_time - user_request[0] > self.window_size:
            user_request.popleft()
        
        if len(user_request) < self.max_limit:
            user_request.append(current_time)
            return True
        return False

#with max limit 5 and window size 10
rate_limiter = RateLimiter(5, 10)

user = "saksham"

for i in range(10):

    if rate_limiter.allow_requests(user):
        print("Request allowed")
    else:
        print("Rate limit exceeded")

    time.sleep(1)