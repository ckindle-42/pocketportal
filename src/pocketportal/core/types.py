"""
Core Type Definitions
=====================

Centralized type definitions for the core module.
Provides type safety and prevents magic strings throughout the codebase.
"""

from enum import Enum


class InterfaceType(str, Enum):
    """
    Enumeration of supported interface types.

    Using Enum instead of magic strings provides:
    - Type safety at development time
    - IDE autocomplete support
    - Easier refactoring
    - Protection against typos
    """

    TELEGRAM = "telegram"
    WEB = "web"
    SLACK = "slack"
    API = "api"
    CLI = "cli"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        """Return the string value for backward compatibility"""
        return self.value


__all__ = ['InterfaceType']
