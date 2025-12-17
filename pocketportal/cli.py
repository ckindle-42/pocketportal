"""
PocketPortal CLI - Unified Command-Line Interface
===================================================

Central entry point for starting interfaces, managing configuration,
and interacting with the PocketPortal agent.
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional
import signal

# Version info
__version__ = "4.1.0"

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_format: str = "text"):
    """Configure logging for the CLI"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    if log_format == "json":
        # JSON logging would go here (requires structlog or similar)
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


async def start_interface(
    interface_type: str,
    config_path: Optional[Path] = None,
    start_all: bool = False
):
    """
    Start one or more interfaces.

    Args:
        interface_type: Type of interface to start ('telegram', 'web', or 'all')
        config_path: Path to configuration file
        start_all: Start all configured interfaces
    """
    try:
        # Import configuration
        from pocketportal.config import load_settings

        # Load settings
        if config_path and config_path.exists():
            settings = load_settings(str(config_path))
            logger.info(f"Loaded configuration from {config_path}")
        else:
            settings = load_settings()
            logger.info("Using default/environment configuration")

        # Import core components
        from pocketportal.core import create_agent_core, SecurityMiddleware
        from pocketportal.interfaces import InterfaceManager

        # Create agent core
        logger.info("Initializing agent core...")
        agent_core = create_agent_core(settings)

        # Wrap with security middleware
        secure_agent = SecurityMiddleware(agent_core, settings.security)
        logger.info("Security middleware enabled")

        # Create interface manager
        manager = InterfaceManager(secure_agent)

        # Register requested interfaces
        if start_all or interface_type == "all":
            # Start all configured interfaces
            if settings.interfaces.telegram:
                from pocketportal.interfaces.telegram_interface import TelegramInterface
                telegram = TelegramInterface(secure_agent, settings.interfaces.telegram)
                manager.register("telegram", telegram)
                logger.info("Registered Telegram interface")

            if settings.interfaces.web:
                from pocketportal.interfaces.web_interface import WebInterface
                web = WebInterface(secure_agent, settings.interfaces.web)
                manager.register("web", web)
                logger.info("Registered Web interface")

        elif interface_type == "telegram":
            if not settings.interfaces.telegram:
                logger.error("Telegram interface not configured")
                sys.exit(1)

            from pocketportal.interfaces.telegram_interface import TelegramInterface
            telegram = TelegramInterface(secure_agent, settings.interfaces.telegram)
            manager.register("telegram", telegram)
            logger.info("Registered Telegram interface")

        elif interface_type == "web":
            if not settings.interfaces.web:
                logger.error("Web interface not configured")
                sys.exit(1)

            from pocketportal.interfaces.web_interface import WebInterface
            web = WebInterface(secure_agent, settings.interfaces.web)
            manager.register("web", web)
            logger.info("Registered Web interface")

        else:
            logger.error(f"Unknown interface type: {interface_type}")
            sys.exit(1)

        if not manager.interfaces:
            logger.error("No interfaces registered. Check your configuration.")
            sys.exit(1)

        # Setup signal handlers for graceful shutdown
        shutdown_event = asyncio.Event()

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start all interfaces
        logger.info("Starting interfaces...")
        await manager.start_all()

        logger.info("✓ PocketPortal is running!")
        logger.info("Press Ctrl+C to stop")

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Graceful shutdown
        logger.info("Shutting down interfaces...")
        await manager.stop_all()
        logger.info("Shutdown complete")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def cmd_start(args):
    """Handle 'start' command"""
    setup_logging(args.log_level, args.log_format)

    config_path = Path(args.config) if args.config else None

    # Run the async start function
    asyncio.run(start_interface(
        interface_type=args.interface,
        config_path=config_path,
        start_all=args.all
    ))


def cmd_validate_config(args):
    """Handle 'validate-config' command"""
    setup_logging(args.log_level, args.log_format)

    try:
        from pocketportal.config import load_settings

        config_path = Path(args.config) if args.config else None

        logger.info("Validating configuration...")
        if config_path:
            settings = load_settings(str(config_path))
        else:
            settings = load_settings()

        errors = settings.validate_required_config()

        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        else:
            logger.info("✓ Configuration is valid")
            logger.info(f"  Models configured: {len(settings.models)}")
            logger.info(f"  Telegram enabled: {settings.interfaces.telegram is not None}")
            logger.info(f"  Web enabled: {settings.interfaces.web is not None}")

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        sys.exit(1)


def cmd_list_tools(args):
    """Handle 'list-tools' command"""
    setup_logging(args.log_level, args.log_format)

    try:
        from pocketportal.tools import registry

        # Discover and load tools
        loaded, failed = registry.discover_and_load()

        print(f"\n{'='*70}")
        print(f"PocketPortal Tools ({loaded} loaded, {failed} failed)")
        print(f"{'='*70}\n")

        # Group by category
        for category, tool_names in sorted(registry.tool_categories.items()):
            if not tool_names:
                continue

            print(f"\n{category.upper()}:")
            print("-" * 70)

            for tool_name in sorted(tool_names):
                tool = registry.get_tool(tool_name)
                if tool:
                    print(f"  • {tool_name}")
                    print(f"    {tool.metadata.description}")

        if failed > 0:
            print(f"\n\n⚠️  {failed} tools failed to load:")
            for failure in registry.get_failed_tools():
                print(f"  • {failure['module']}: {failure['error']}")

    except Exception as e:
        logger.error(f"Failed to list tools: {e}", exc_info=True)
        sys.exit(1)


def cmd_version(args):
    """Handle 'version' command"""
    print(f"PocketPortal {__version__}")
    print("Privacy-first, interface-agnostic AI agent platform")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="pocketportal",
        description="PocketPortal - Modular AI Agent Platform",
        epilog="For more information, visit: https://github.com/ckindle-42/pocketportal"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # Global options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )

    parser.add_argument(
        "--log-format",
        choices=["text", "json"],
        default="text",
        help="Log output format"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start one or more interfaces"
    )
    start_parser.add_argument(
        "--interface",
        choices=["telegram", "web", "all"],
        default="telegram",
        help="Interface to start (default: telegram)"
    )
    start_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    start_parser.add_argument(
        "--all",
        action="store_true",
        help="Start all configured interfaces"
    )
    start_parser.set_defaults(func=cmd_start)

    # Validate config command
    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate configuration file"
    )
    validate_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    validate_parser.set_defaults(func=cmd_validate_config)

    # List tools command
    list_tools_parser = subparsers.add_parser(
        "list-tools",
        help="List all available tools"
    )
    list_tools_parser.set_defaults(func=cmd_list_tools)

    # Version command (also handled by --version)
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information"
    )
    version_parser.set_defaults(func=cmd_version)

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
