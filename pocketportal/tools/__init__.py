"""
Enhanced Tool Registry - Auto-discovery and management of agent tools
Includes validation, error handling, and performance tracking
"""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sys

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionStats:
    """Statistics for tool execution"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    last_execution: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    @property
    def average_execution_time(self) -> float:
        if self.successful_executions == 0:
            return 0.0
        return self.total_execution_time / self.successful_executions


class ToolRegistry:
    """Enhanced registry for discovering and managing tools"""

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.tool_categories: Dict[str, List[str]] = {
            'data': [],
            'system': [],
            'web': [],
            'audio': [],
            'dev': [],
            'automation': [],
            'knowledge': []
        }
        self.tool_stats: Dict[str, ToolExecutionStats] = {}
        self.failed_tools: List[Dict[str, str]] = []

    def discover_and_load(self) -> tuple[int, int]:
        """
        Auto-discover and load all tools from tool directories.
        Uses pkgutil.walk_packages for dynamic discovery.
        Returns (loaded_count, failed_count)
        """

        tools_dir = Path(__file__).parent
        loaded = 0
        failed = 0

        # Dynamic tool discovery using pkgutil
        # Walk through all subdirectories and discover tool classes
        logger.info(f"Scanning for tools in {tools_dir}")

        # Import base_tool to get BaseTool class for isinstance check
        from .base_tool import BaseTool

        # Walk through all packages in the tools directory
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=[str(tools_dir)],
            prefix='pocketportal.tools.'
        ):
            # Skip __init__ files and base_tool
            if modname.endswith('__init__') or modname.endswith('base_tool'):
                continue

            # Skip packages (directories), only process modules (files)
            if ispkg:
                continue

            module_path = modname
            try:
                # Import module
                module = importlib.import_module(module_path)

                # Find all classes in module that inherit from BaseTool
                tool_classes = []
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a subclass of BaseTool (but not BaseTool itself)
                    if (issubclass(obj, BaseTool) and
                        obj is not BaseTool and
                        obj.__module__ == module_path):
                        tool_classes.append((name, obj))

                if not tool_classes:
                    # No tool classes found in this module, skip silently
                    continue

                # Load each tool class found in the module
                for class_name, tool_class in tool_classes:
                    try:
                        # Instantiate tool
                        tool_instance = tool_class()

                        # Validate tool has required attributes
                        if not hasattr(tool_instance, 'metadata'):
                            raise AttributeError(f"Tool {class_name} missing 'metadata' attribute")

                        if not hasattr(tool_instance, 'execute'):
                            raise AttributeError(f"Tool {class_name} missing 'execute' method")

                        # Register tool
                        tool_name = tool_instance.metadata.name
                        self.tools[tool_name] = tool_instance

                        # Initialize stats
                        self.tool_stats[tool_name] = ToolExecutionStats()

                        # Add to category
                        category = tool_instance.metadata.category.value
                        if category in self.tool_categories:
                            self.tool_categories[category].append(tool_name)
                        else:
                            # Create new category if not exists
                            self.tool_categories[category] = [tool_name]

                        loaded += 1
                        logger.info(f"Loaded tool: {tool_name} ({category}) from {module_path}")

                    except Exception as e:
                        failed += 1
                        error_msg = f"Failed to instantiate {class_name} from {module_path}: {str(e)}"
                        logger.error(f"Error: {error_msg}")
                        self.failed_tools.append({
                            'module': module_path,
                            'class': class_name,
                            'error': error_msg,
                            'type': type(e).__name__
                        })

            except ImportError as e:
                failed += 1
                error_msg = f"Import failed for {module_path}: {str(e)}"
                logger.error(f"Import error: {error_msg}")
                self.failed_tools.append({
                    'module': module_path,
                    'class': 'unknown',
                    'error': error_msg,
                    'type': 'ImportError'
                })

            except Exception as e:
                failed += 1
                error_msg = f"Unexpected error loading {module_path}: {str(e)}"
                logger.error(f"Unexpected error: {error_msg}")
                self.failed_tools.append({
                    'module': module_path,
                    'class': 'unknown',
                    'error': error_msg,
                    'type': type(e).__name__
                })

        # Log summary
        logger.info(f"Tool registry: {loaded} loaded, {failed} failed")

        if failed > 0:
            logger.warning(f"Failed tools: {[t['module'] for t in self.failed_tools]}")

        return loaded, failed

    def get_tool(self, name: str) -> Optional[Any]:
        """Get tool by name"""
        return self.tools.get(name)

    def get_all_tools(self) -> List[Any]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_tools_by_category(self, category: str) -> List[Any]:
        """Get tools by category"""
        tool_names = self.tool_categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """
        Get list of tool metadata for display purposes.
        Returns structured data about each tool.
        """
        tool_list = []

        for tool in self.tools.values():
            metadata = tool.metadata
            stats = self.tool_stats.get(metadata.name, ToolExecutionStats())

            tool_list.append({
                'name': metadata.name,
                'description': metadata.description,
                'category': metadata.category.value,
                'requires_confirmation': metadata.requires_confirmation,
                'version': metadata.version,
                'async_capable': metadata.async_capable,
                'stats': {
                    'executions': stats.total_executions,
                    'success_rate': stats.success_rate,
                    'avg_time': stats.average_execution_time
                }
            })

        return tool_list

    def record_execution(self, tool_name: str, success: bool, execution_time: float):
        """Record tool execution statistics"""
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = ToolExecutionStats()

        stats = self.tool_stats[tool_name]
        stats.total_executions += 1
        stats.last_execution = datetime.now()

        if success:
            stats.successful_executions += 1
            stats.total_execution_time += execution_time
        else:
            stats.failed_executions += 1

    def get_tool_stats(self, tool_name: str) -> Optional[ToolExecutionStats]:
        """Get statistics for a specific tool"""
        return self.tool_stats.get(tool_name)

    def get_all_stats(self) -> Dict[str, ToolExecutionStats]:
        """Get statistics for all tools"""
        return self.tool_stats.copy()

    def get_failed_tools(self) -> List[Dict[str, str]]:
        """Get list of tools that failed to load"""
        return self.failed_tools.copy()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all tools.
        Returns health status and any issues found.
        """
        health_report = {
            'status': 'healthy',
            'total_tools': len(self.tools),
            'failed_loads': len(self.failed_tools),
            'tools_never_executed': [],
            'tools_high_failure_rate': [],
            'timestamp': datetime.now().isoformat()
        }

        # Check for tools that have never been executed
        for tool_name, stats in self.tool_stats.items():
            if stats.total_executions == 0:
                health_report['tools_never_executed'].append(tool_name)

        # Check for tools with high failure rates
        for tool_name, stats in self.tool_stats.items():
            if stats.total_executions >= 10 and stats.success_rate < 0.5:
                health_report['tools_high_failure_rate'].append({
                    'name': tool_name,
                    'success_rate': stats.success_rate,
                    'executions': stats.total_executions
                })

        # Determine overall status
        if health_report['failed_loads'] > 3:
            health_report['status'] = 'degraded'

        if health_report['tools_high_failure_rate']:
            health_report['status'] = 'degraded'

        return health_report

    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters before tool execution.
        Returns (is_valid, error_message)
        """
        tool = self.get_tool(tool_name)

        if not tool:
            return False, f"Tool '{tool_name}' not found"

        # Check if tool has validate_parameters method
        if hasattr(tool, 'validate_parameters'):
            try:
                return tool.validate_parameters(parameters)
            except Exception as e:
                return False, f"Validation error: {str(e)}"

        # Basic validation if no custom validator
        required_params = tool.metadata.parameters
        for param_name, param_spec in required_params.items():
            if param_spec.get('required', False) and param_name not in parameters:
                return False, f"Missing required parameter: {param_name}"

        return True, None


# Global registry instance
registry = ToolRegistry()
