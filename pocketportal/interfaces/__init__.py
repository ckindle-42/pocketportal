"""
Interfaces module - Adapters for different platforms
======================================================

This module provides interface adapters for various platforms (Telegram, Web, etc.)
Each interface is organized in its own sub-package for better modularity.

Structure:
    interfaces/
        base.py              # Base interface definitions
        telegram/            # Telegram-specific interface
            __init__.py      # Main interface logic
            ui.py            # Formatting and presentation
        web/                 # Web interface (FastAPI)
            __init__.py      # Main web app

Usage:
    from pocketportal.interfaces import BaseInterface
    from pocketportal.interfaces.telegram import TelegramInterface
    from pocketportal.interfaces.web import app
"""

from .base import BaseInterface, InterfaceManager, Message, Response

__all__ = [
    'BaseInterface',
    'InterfaceManager',
    'Message',
    'Response',
]

# Interface sub-packages are imported individually as needed:
# from pocketportal.interfaces.telegram import TelegramInterface
# from pocketportal.interfaces.web import app

