"""
Configuration Management Module
================================

Centralized configuration loading and validation.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import os
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    backend: str
    capabilities: list
    speed_class: str


@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 20
    max_file_size_mb: int = 10
    allowed_commands: list = None


@dataclass
class PocketPortalConfig:
    """Main configuration class"""
    models: Dict[str, ModelConfig]
    security: SecurityConfig
    interfaces: Dict[str, Any]
    tools: Dict[str, Any]


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file or environment variables

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary
    """
    config = {}

    # Load from file if provided
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)

    # Override with environment variables
    if 'OLLAMA_BASE_URL' in os.environ:
        config.setdefault('backends', {})
        config['backends']['ollama_url'] = os.environ['OLLAMA_BASE_URL']

    if 'TELEGRAM_BOT_TOKEN' in os.environ:
        config.setdefault('interfaces', {})
        config['interfaces']['telegram_token'] = os.environ['TELEGRAM_BOT_TOKEN']

    return config


__all__ = [
    'ModelConfig',
    'SecurityConfig',
    'PocketPortalConfig',
    'load_config',
    # New Pydantic-based settings (recommended)
    'Settings',
    'load_settings',
]

# Import new Pydantic settings
try:
    from .settings import Settings, load_settings
except ImportError:
    # Fallback if pydantic-settings not installed
    Settings = None
    load_settings = None
