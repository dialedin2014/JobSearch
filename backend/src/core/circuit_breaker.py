"""
Circuit Breaker Manager for API resilience.

Provides centralized management of circuit breakers for external API calls
to prevent cascading failures.
"""

from circuitbreaker import CircuitBreaker, CircuitBreakerError
from typing import Dict, Callable, Any
import logging

logger = logging.getLogger(__name__)


class CircuitBreakerManager:
    """
    Centralized circuit breaker management.

    Manages circuit breakers for different services to prevent cascading
    failures when external APIs are unavailable.

    Attributes:
        breakers: Dictionary of service name to CircuitBreaker instance
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker manager.

        Args:
            failure_threshold: Consecutive failures before opening circuit
            recovery_timeout: Seconds to wait in open state before trying again
        """
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service.

        Args:
            service_name: Name of the service (e.g., 'github', 'twitter')

        Returns:
            CircuitBreaker instance for the service
        """
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(
                failure_threshold=self.failure_threshold,
                recovery_timeout=self.recovery_timeout,
                name=service_name
            )
            logger.info(
                f"Created circuit breaker for {service_name}: "
                f"threshold={self.failure_threshold}, "
                f"recovery={self.recovery_timeout}s"
            )

        return self.breakers[service_name]

    def wrap(self, service_name: str, func: Callable) -> Callable:
        """
        Wrap a function with circuit breaker protection.

        Args:
            service_name: Name of the service
            func: Function to protect

        Returns:
            Wrapped function with circuit breaker
        """
        breaker = self.get_breaker(service_name)
        return breaker(func)

    def get_state(self, service_name: str) -> str:
        """
        Get current state of a circuit breaker.

        Args:
            service_name: Name of the service

        Returns:
            State string: 'closed', 'open', or 'half_open'
        """
        if service_name not in self.breakers:
            return 'closed'

        breaker = self.breakers[service_name]
        return breaker.current_state

    def reset(self, service_name: str) -> None:
        """
        Manually reset a circuit breaker.

        Args:
            service_name: Name of the service
        """
        if service_name in self.breakers:
            # Circuit breakers don't have a direct reset, but we can create a new one
            self.breakers[service_name] = CircuitBreaker(
                failure_threshold=self.failure_threshold,
                recovery_timeout=self.recovery_timeout,
                name=service_name
            )
            logger.info(f"Reset circuit breaker for {service_name}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all circuit breakers.

        Returns:
            Dictionary of service names to their states
        """
        return {
            name: {
                'state': self.get_state(name),
                'failure_count': breaker.failure_count if hasattr(breaker, 'failure_count') else 0,
            }
            for name, breaker in self.breakers.items()
        }


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager(
    failure_threshold=5,
    recovery_timeout=60
)
