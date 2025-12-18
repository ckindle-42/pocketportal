"""
Lifecycle Management - Bootstrap and Runtime Orchestration
===========================================================

This module provides lifecycle management for PocketPortal, handling:
- Application bootstrap (loading config, initializing DI container)
- Starting the event bus and core services
- OS signal handling (SIGINT/SIGTERM)
- Graceful shutdown

This decouples lifecycle concerns from the Engine, which should
purely process input/output.

Architecture:
    CLI/Main → Runtime → Engine
                 ├─ Config Loading
                 ├─ DI Container
                 ├─ Event Bus
                 ├─ Signal Handling
                 └─ Shutdown Sequence
"""

import asyncio
import logging
import signal
import sys
from typing import Optional, Callable, List
from dataclasses import dataclass, field

from pocketportal.config.settings import Settings, load_settings
from pocketportal.core import create_agent_core, AgentCore
from pocketportal.core.event_broker import create_event_broker, EventBroker
from pocketportal.security import SecurityMiddleware
from pocketportal.core.structured_logger import get_logger

logger = get_logger('Lifecycle')


@dataclass
class RuntimeContext:
    """
    Runtime context containing all initialized components

    This serves as the DI container for the application.
    """
    settings: Settings
    event_broker: EventBroker
    agent_core: AgentCore
    secure_agent: SecurityMiddleware
    shutdown_callbacks: List[Callable] = field(default_factory=list)


class Runtime:
    """
    Runtime orchestrator for PocketPortal

    Responsibilities:
    1. Bootstrap: Load config, initialize services
    2. Signal handling: Graceful shutdown on SIGINT/SIGTERM
    3. Lifecycle management: Start/stop services
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize runtime

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.context: Optional[RuntimeContext] = None
        self._shutdown_event = asyncio.Event()
        self._initialized = False

    async def bootstrap(self) -> RuntimeContext:
        """
        Bootstrap the application

        Returns:
            RuntimeContext with all initialized components
        """
        if self._initialized:
            logger.warning("Runtime already initialized")
            return self.context

        logger.info("Bootstrapping PocketPortal runtime")

        # Step 1: Load configuration
        logger.info("Loading configuration")
        if self.config_path:
            settings = load_settings(self.config_path)
        else:
            settings = load_settings()

        # Step 2: Initialize event broker
        logger.info("Initializing event broker")
        event_broker = create_event_broker(
            backend="memory",
            max_history=1000
        )

        # Step 3: Create agent core
        logger.info("Creating agent core")
        agent_core = create_agent_core(settings)

        # Step 4: Wrap with security middleware
        logger.info("Initializing security middleware")
        secure_agent = SecurityMiddleware(
            agent_core,
            enable_rate_limiting=True,
            enable_input_sanitization=True
        )

        # Step 5: Setup signal handlers
        self._setup_signal_handlers()

        # Create runtime context
        self.context = RuntimeContext(
            settings=settings,
            event_broker=event_broker,
            agent_core=agent_core,
            secure_agent=secure_agent
        )

        self._initialized = True
        logger.info("Runtime bootstrap completed")

        return self.context

    def _setup_signal_handlers(self):
        """Setup OS signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            """Handle shutdown signals"""
            signal_name = signal.Signals(signum).name
            logger.info(f"Received {signal_name}, initiating graceful shutdown")
            self._shutdown_event.set()

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.debug("Signal handlers registered")

    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()

    async def shutdown(self):
        """
        Graceful shutdown sequence

        Stops all services in reverse order of initialization.
        """
        if not self._initialized:
            logger.warning("Runtime not initialized, nothing to shutdown")
            return

        logger.info("Starting graceful shutdown")

        # Run custom shutdown callbacks
        for callback in self.context.shutdown_callbacks:
            try:
                logger.debug(f"Executing shutdown callback: {callback.__name__}")
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}", exc_info=True)

        # Cleanup agent core
        try:
            logger.info("Cleaning up agent core")
            await self.context.secure_agent.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up agent core: {e}", exc_info=True)

        # Clear event history
        try:
            logger.info("Clearing event history")
            await self.context.event_broker.clear_history()
        except Exception as e:
            logger.error(f"Error clearing event history: {e}", exc_info=True)

        self._initialized = False
        logger.info("Shutdown completed")

    def register_shutdown_callback(self, callback: Callable):
        """
        Register a callback to be executed during shutdown

        Args:
            callback: Function or coroutine to execute
        """
        if self.context:
            self.context.shutdown_callbacks.append(callback)
        else:
            logger.warning("Cannot register shutdown callback: Runtime not initialized")


async def run_with_lifecycle(
    main_task: Callable[[RuntimeContext], None],
    config_path: Optional[str] = None
):
    """
    Helper function to run an application with proper lifecycle management

    Args:
        main_task: Async function that runs the main application logic
        config_path: Optional path to configuration file

    Example:
        async def main(ctx: RuntimeContext):
            # Your application logic here
            await my_interface.start()

        asyncio.run(run_with_lifecycle(main))
    """
    runtime = Runtime(config_path)

    try:
        # Bootstrap
        context = await runtime.bootstrap()

        # Run main task
        await main_task(context)

        # Wait for shutdown signal
        await runtime.wait_for_shutdown()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Graceful shutdown
        await runtime.shutdown()
