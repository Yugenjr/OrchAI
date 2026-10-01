import pytest
from orchai.auth.rate_limit import RateLimiter
import time

def test_rate_limiting_enforcement():
    limiter = RateLimiter()
    limiter.reset()
    
    # AUTH_ATTEMPT limit is 5 per 60s
    identifier = "user_test"
    for i in range(5):
        assert limiter.check_rate_limit(identifier, "AUTH_ATTEMPT") is True
        
    # 6th should fail
    assert limiter.check_rate_limit(identifier, "AUTH_ATTEMPT") is False
    
    # Different action should work
    assert limiter.check_rate_limit(identifier, "TASK_CREATE") is True
    
    # Different user should work
    assert limiter.check_rate_limit("user_other", "AUTH_ATTEMPT") is True
