"""
Custom Exceptions for PocketPortal 4.0
======================================

Structured error handling allows interfaces to handle errors appropriately
based on type rather than parsing strings.
"""

from typing import Optional, Dict, Any


class PocketPortalError(Exception):
    """Base exception for all PocketPortal errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class PolicyViolationError(PocketPortalError):
    """Raised when security policy is violated"""
    pass


class ModelQuotaExceededError(PocketPortalError):
    """Raised when model quota or rate limit is exceeded"""
    pass


class ModelNotAvailableError(PocketPortalError):
    """Raised when no models are available"""
    pass


class ToolExecutionError(PocketPortalError):
    """Raised when tool execution fails"""

    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.tool_name = tool_name


class AuthorizationError(PocketPortalError):
    """Raised when user is not authorized"""
    pass


class RateLimitError(PocketPortalError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.retry_after = retry_after


class ContextNotFoundError(PocketPortalError):
    """Raised when conversation context is not found"""
    pass


class ValidationError(PocketPortalError):
    """Raised when input validation fails"""
    pass
