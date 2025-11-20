"""
Retry utilities with exponential backoff for API calls
Handles rate limiting and transient errors
"""

import asyncio
import functools
import time
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    MAX_RETRIES = 5
    INITIAL_DELAY = 2.0  # seconds
    MAX_DELAY = 60.0  # seconds
    BACKOFF_MULTIPLIER = 2.0
    RETRY_STATUS_CODES = [429, 503, 500]  # Rate limit, service unavailable, internal error


def async_retry_with_backoff(
    max_retries: int = RetryConfig.MAX_RETRIES,
    initial_delay: float = RetryConfig.INITIAL_DELAY,
    max_delay: float = RetryConfig.MAX_DELAY,
    backoff_multiplier: float = RetryConfig.BACKOFF_MULTIPLIER
):
    """
    Decorator for async functions that implements exponential backoff retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries
        backoff_multiplier: Multiplier for exponential backoff
    
    Usage:
        @async_retry_with_backoff(max_retries=3)
        async def my_api_call():
            return await client.generate_content(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    error_msg = str(e)
                    
                    # Check if this is a retriable error
                    is_rate_limit = '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg
                    is_server_error = '503' in error_msg or '500' in error_msg
                    
                    if not (is_rate_limit or is_server_error):
                        # Not a retriable error, raise immediately
                        logger.error(f"Non-retriable error in {func.__name__}: {error_msg}")
                        raise
                    
                    if attempt < max_retries:
                        # Calculate delay with jitter
                        jitter = delay * 0.1  # 10% jitter
                        actual_delay = min(delay + jitter, max_delay)
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}. "
                            f"Retrying in {actual_delay:.2f}s. Error: {error_msg[:100]}"
                        )
                        
                        await asyncio.sleep(actual_delay)
                        delay *= backoff_multiplier
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}. "
                            f"Final error: {error_msg[:100]}"
                        )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


class RateLimiter:
    """Simple rate limiter to prevent API quota exhaustion"""
    
    def __init__(self, calls_per_minute: int = 15):
        """
        Initialize rate limiter
        
        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute  # seconds between calls
        self.last_call_time = 0.0
    
    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            wait_time = self.min_interval - time_since_last_call
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        self.last_call_time = time.time()
