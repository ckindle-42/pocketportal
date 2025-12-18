"""
Settings Schema
================

Pydantic models for PocketPortal configuration.

This provides:
- Type validation for all config fields
- Default values
- Environment variable support
- Documentation for each setting
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from pathlib import Path


class InterfaceConfig(BaseModel):
    """Configuration for interfaces (Telegram, Web, etc.)"""

    telegram: bool = Field(
        default=False,
        description="Enable Telegram interface"
    )
    web: bool = Field(
        default=False,
        description="Enable Web interface"
    )
    api: bool = Field(
        default=False,
        description="Enable REST API interface"
    )

    # Telegram-specific settings
    telegram_token: Optional[str] = Field(
        default=None,
        description="Telegram bot token"
    )
    telegram_allowed_users: List[int] = Field(
        default_factory=list,
        description="List of allowed Telegram user IDs (empty = allow all)"
    )

    # Web-specific settings
    web_host: str = Field(
        default="0.0.0.0",
        description="Web interface host"
    )
    web_port: int = Field(
        default=8000,
        description="Web interface port",
        ge=1,
        le=65535
    )


class SecurityConfig(BaseModel):
    """Security and rate limiting configuration"""

    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=10,
        description="Max requests per window",
        ge=1
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds",
        ge=1
    )

    sandbox_enabled: bool = Field(
        default=False,
        description="Enable Docker sandbox for untrusted code"
    )
    sandbox_timeout_seconds: int = Field(
        default=30,
        description="Sandbox execution timeout",
        ge=1,
        le=300
    )


class LLMConfig(BaseModel):
    """LLM backend configuration"""

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    default_model: str = Field(
        default="llama2",
        description="Default LLM model"
    )
    temperature: float = Field(
        default=0.7,
        description="LLM temperature (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    max_tokens: int = Field(
        default=2000,
        description="Max tokens per response",
        ge=100,
        le=100000
    )
    timeout_seconds: int = Field(
        default=60,
        description="LLM request timeout",
        ge=1,
        le=300
    )


class ObservabilityConfig(BaseModel):
    """Observability and monitoring configuration"""

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )

    # OpenTelemetry
    telemetry_enabled: bool = Field(
        default=False,
        description="Enable OpenTelemetry tracing"
    )
    telemetry_endpoint: Optional[str] = Field(
        default=None,
        description="OTLP exporter endpoint (e.g., http://localhost:4317)"
    )
    telemetry_service_name: str = Field(
        default="pocketportal",
        description="Service name for tracing"
    )

    # Metrics
    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    metrics_port: int = Field(
        default=9090,
        description="Prometheus metrics port",
        ge=1,
        le=65535
    )

    # Health checks
    health_checks_enabled: bool = Field(
        default=True,
        description="Enable health check endpoints"
    )

    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()


class JobQueueConfig(BaseModel):
    """Job queue configuration"""

    enabled: bool = Field(
        default=True,
        description="Enable async job queue"
    )
    worker_count: int = Field(
        default=4,
        description="Number of concurrent workers",
        ge=1,
        le=100
    )
    max_retries: int = Field(
        default=3,
        description="Max retry attempts for failed jobs",
        ge=0,
        le=10
    )
    stale_job_timeout_minutes: int = Field(
        default=30,
        description="Timeout for detecting stale jobs",
        ge=1,
        le=1440
    )
    cleanup_interval_hours: int = Field(
        default=24,
        description="Interval for cleaning up old jobs",
        ge=1,
        le=168
    )


class SettingsSchema(BaseModel):
    """
    Root settings schema for PocketPortal.

    This is the top-level configuration object that contains all settings.
    """

    # Sub-configurations
    interfaces: InterfaceConfig = Field(
        default_factory=InterfaceConfig,
        description="Interface configurations"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security settings"
    )
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM backend settings"
    )
    observability: ObservabilityConfig = Field(
        default_factory=ObservabilityConfig,
        description="Observability settings"
    )
    job_queue: JobQueueConfig = Field(
        default_factory=JobQueueConfig,
        description="Job queue settings"
    )

    # General settings
    data_dir: Path = Field(
        default=Path.home() / ".pocketportal",
        description="Data directory for persistent storage"
    )

    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "forbid"  # Reject unknown fields
