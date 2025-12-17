"""
Model Context Protocol (MCP)
=============================

Bidirectional MCP support:
- MCP Client: Connect to other MCP servers
- MCP Server: Expose PocketPortal tools via MCP
- MCP Registry: Manage MCP server configurations

This enables full mesh networking between PocketPortal
and other MCP-compatible applications.
"""

from .mcp_connector import MCPConnectorTool
from .mcp_registry import MCPRegistry

# Server is optional (requires MCP SDK)
try:
    from .mcp_server import MCPServer, start_mcp_server
    MCP_SERVER_AVAILABLE = True
except ImportError:
    MCP_SERVER_AVAILABLE = False
    MCPServer = None
    start_mcp_server = None

__all__ = [
    'MCPConnectorTool',
    'MCPRegistry',
    'MCPServer',
    'start_mcp_server',
    'MCP_SERVER_AVAILABLE',
]
