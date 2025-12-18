"""
Core Interfaces - Abstract interfaces and contracts
===================================================

This module contains the core contracts and interfaces that define
how different components of the system interact.
"""

from .tool import (
    BaseTool,
    ToolMetadata,
    ToolParameter,
    ToolCategory,
)

__all__ = [
    'BaseTool',
    'ToolMetadata',
    'ToolParameter',
    'ToolCategory',
]
