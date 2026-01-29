import time
from threading import Lock


class CircuitBreaker:
    def __init__(self, fail_threshold=5, reset_timeout=30):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.state = 'CLOSED'
        self.last_failure = 0
        self._lock = Lock()

    def record_success(self):
        with self._lock:
            self.fail_count = 0
            self.state = 'CLOSED'

    def record_failure(self):
        with self._lock:
            self.fail_count += 1
            self.last_failure = time.time()
            if self.fail_count >= self.fail_threshold:
                self.state = 'OPEN'

    def allow(self):
        with self._lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure > self.reset_timeout:
                    self.state = 'HALF'
                    return True
                return False
            return True


# simple module-level breaker for external callbacks
outgoing_breaker = CircuitBreaker(fail_threshold=int(__import__('os').getenv('CB_FAIL_THRESHOLD','5')), reset_timeout=int(__import__('os').getenv('CB_RESET_TIMEOUT','30')))
