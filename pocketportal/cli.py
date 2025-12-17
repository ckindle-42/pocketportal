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
__version__ = "4.1.1"

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_format: str = "text"):
    """Configure logging for the CLI"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    if log_format == "json":
        # Use structured logging format (compatible with core engine)
        # The structured logger outputs JSON messages directly
        fmt = "%(message)s"  # Just output the message (which will be JSON from StructuredLogger)
    else:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True  # Ensure this overrides any previous basicConfig calls
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
                telegram = TelegramInterface(secure_agent, settings)
                manager.register("telegram", telegram)
                logger.info("Registered Telegram interface")

            if settings.interfaces.web:
                from pocketportal.interfaces.web_interface import WebInterface
                web = WebInterface(secure_agent, settings)
                manager.register("web", web)
                logger.info("Registered Web interface")

        elif interface_type == "telegram":
            if not settings.interfaces.telegram:
                logger.error("Telegram interface not configured")
                sys.exit(1)

            from pocketportal.interfaces.telegram_interface import TelegramInterface
            telegram = TelegramInterface(secure_agent, settings)
            manager.register("telegram", telegram)
            logger.info("Registered Telegram interface")

        elif interface_type == "web":
            if not settings.interfaces.web:
                logger.error("Web interface not configured")
                sys.exit(1)

            from pocketportal.interfaces.web_interface import WebInterface
            web = WebInterface(secure_agent, settings)
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


def cmd_verify(args):
    """Handle 'verify' command - verify installation"""
    setup_logging(args.log_level, args.log_format)

    from pathlib import Path
    import shutil

    # Colors for output
    class Colors:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        END = '\033[0m'
        BOLD = '\033[1m'

    def print_success(text):
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")

    def print_error(text):
        print(f"{Colors.RED}✗ {text}{Colors.END}")

    def print_warning(text):
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

    def print_header(text):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

    results = []

    # Check 1: Python version
    print_header("Python Version")
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 11:
        print_success(f"Python {major}.{minor}.{sys.version_info.micro}")
        results.append(True)
    else:
        print_error(f"Python {major}.{minor} - Need 3.11 or higher")
        results.append(False)

    # Check 2: Virtual environment
    print_header("Virtual Environment")
    if sys.prefix != sys.base_prefix:
        print_success(f"Virtual environment: {sys.prefix}")
        results.append(True)
    else:
        print_warning("Not in virtual environment (recommended but optional)")
        results.append(True)

    # Check 3: Package structure
    print_header("Package Structure")
    required_modules = [
        'pocketportal.core',
        'pocketportal.config',
        'pocketportal.tools',
        'pocketportal.interfaces',
    ]

    all_modules_exist = True
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            print_error(f"Missing module: {module_name}")
            all_modules_exist = False

    if all_modules_exist:
        print_success(f"All {len(required_modules)} core modules exist")
        results.append(True)
    else:
        results.append(False)

    # Check 4: Core dependencies
    print_header("Core Dependencies")
    core_deps = [
        ('telegram', 'python-telegram-bot'),
        ('dotenv', 'python-dotenv'),
        ('pydantic', 'pydantic'),
        ('aiohttp', 'aiohttp'),
        ('cryptography', 'cryptography'),
    ]

    all_installed = True
    for module_name, package_name in core_deps:
        try:
            __import__(module_name)
        except ImportError:
            print_error(f"Missing: {package_name}")
            all_installed = False

    if all_installed:
        print_success(f"All {len(core_deps)} core dependencies installed")
        results.append(True)
    else:
        results.append(False)

    # Check 5: Configuration
    print_header("Configuration")
    try:
        from pocketportal.config import load_settings
        settings = load_settings()
        errors = settings.validate_required_config()

        if errors:
            for error in errors:
                print_error(error)
            results.append(False)
        else:
            print_success("Configuration is valid")
            print_success(f"  Models configured: {len(settings.models)}")
            print_success(f"  Telegram enabled: {settings.interfaces.telegram is not None}")
            print_success(f"  Web enabled: {settings.interfaces.web is not None}")
            results.append(True)
    except Exception as e:
        print_error(f"Configuration error: {e}")
        results.append(False)

    # Check 6: Tools system
    print_header("Tools System")
    try:
        from pocketportal.tools import registry
        loaded, failed = registry.discover_and_load()

        if loaded > 0:
            print_success(f"Tools loaded: {loaded} loaded, {failed} failed")
            results.append(True)
        else:
            print_warning("No tools loaded yet")
            results.append(True)
    except Exception as e:
        print_error(f"Tool system error: {e}")
        results.append(False)

    # Check 7: Disk space
    print_header("Disk Space")
    try:
        total, used, free = shutil.disk_usage(Path.home())
        free_gb = free // (2**30)

        if free_gb > 10:
            print_success(f"Disk space: {free_gb}GB free")
            results.append(True)
        else:
            print_warning(f"Low disk space: {free_gb}GB free")
            results.append(True)
    except Exception as e:
        print_warning(f"Disk space check failed: {e}")
        results.append(True)

    # Check 8: System memory (if psutil available)
    print_header("System Memory")
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total // (2**30)
        available_gb = mem.available // (2**30)

        print_success(f"Memory: {available_gb}GB available / {total_gb}GB total")
        results.append(True)
    except ImportError:
        print_warning("psutil not installed (memory check skipped)")
        results.append(True)
    except Exception as e:
        print_warning(f"Memory check failed: {e}")
        results.append(True)

    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)

    print(f"Total checks: {len(results)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")

    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if failed == 0:
        print_success("ALL CHECKS PASSED!")
        print(f"\n{Colors.GREEN}PocketPortal is ready to use{Colors.END}")
    else:
        print_error("SOME CHECKS FAILED")
        print(f"\n{Colors.YELLOW}Please fix the issues above before proceeding{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    sys.exit(0 if failed == 0 else 1)


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

    # Verify command
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify installation and configuration"
    )
    verify_parser.set_defaults(func=cmd_verify)

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
