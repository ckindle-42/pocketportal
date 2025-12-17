"""
Interfaces module - Adapters for different platforms
"""

from .base import BaseInterface, InterfaceManager, Message, Response

__all__ = [
    'BaseInterface',
    'InterfaceManager',
    'Message',
    'Response',
]

# Interfaces will be imported individually as needed
# from .telegram_interface import TelegramInterface
# from .web_interface import app (FastAPI)
