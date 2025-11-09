"""
Rate limiting implementation using token bucket algorithm.

This module provides rate limiting for API endpoints and external service calls.
"""

import time
from threading import Lock
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation.
    
    Attributes:
        capacity: Maximum number of tokens in the bucket
        refill_rate: Number of tokens added per second
        tokens: Current number of tokens available
        last_refill: Timestamp of last refill
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize rate limiter.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            bool: True if tokens were acquired, False otherwise
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_acquire(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """
        Wait until tokens are available, then acquire.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if tokens were acquired, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.acquire(tokens):
                return True
            time.sleep(0.1)
        logger.warning(f"Rate limiter timeout after {timeout}s")
        return False


class RateLimiterManager:
    """
    Manages multiple rate limiters for different services.
    """

    def __init__(self):
        """Initialize rate limiter manager."""
        self.limiters: Dict[str, TokenBucketRateLimiter] = {}
        self.lock = Lock()

    def get_or_create(self, key: str, capacity: int, refill_rate: float) -> TokenBucketRateLimiter:
        """
        Get existing rate limiter or create new one.
        
        Args:
            key: Unique identifier for this rate limiter
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
            
        Returns:
            TokenBucketRateLimiter: Rate limiter instance
        """
        with self.lock:
            if key not in self.limiters:
                self.limiters[key] = TokenBucketRateLimiter(capacity, refill_rate)
            return self.limiters[key]


# Global rate limiter manager instance
rate_limiter_manager = RateLimiterManager()
