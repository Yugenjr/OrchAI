import time
from collections import defaultdict
import threading

class RateLimiter:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RateLimiter, cls).__new__(cls)
                cls._instance._init()
            return cls._instance
            
    def _init(self):
        # Maps (tenant_id, action) to list of timestamps
        self.history = defaultdict(list)
        # Limits: action -> (max_requests, window_seconds)
        self.limits = {
            "TASK_CREATE": (10, 60),
            "API_REQUEST": (100, 60),
            "AUTH_ATTEMPT": (5, 60),
            "TOOL_APPROVE": (20, 60)
        }

    def check_rate_limit(self, identifier: str, action: str) -> bool:
        if action not in self.limits:
            return True # No limit
            
        max_req, window = self.limits[action]
        now = time.time()
        
        with self._lock:
            key = f"{identifier}:{action}"
            # Clean old entries
            self.history[key] = [t for t in self.history[key] if now - t < window]
            
            if len(self.history[key]) >= max_req:
                return False
                
            self.history[key].append(now)
            return True

    def reset(self):
        with self._lock:
            self.history.clear()
