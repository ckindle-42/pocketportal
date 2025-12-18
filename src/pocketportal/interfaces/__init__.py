"""
Interfaces module - Adapters for different platforms
====================================================

Modularized interface packages for better organization:
- telegram/: Telegram bot interface and renderers
- web/: FastAPI + WebSocket web interface
"""

from pocketportal.core.interfaces.agent_interface import BaseInterface, InterfaceManager, Message, Response
from .telegram import TelegramInterface

__all__ = [
    'BaseInterface',
    'InterfaceManager',
    'Message',
    'Response',
    'TelegramInterface',
]
