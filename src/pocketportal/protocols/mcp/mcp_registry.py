"""
MCP Server Registry
Manages registered MCP servers and their configurations
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class MCPServerRegistry:
    """Registry for MCP server configurations"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / ".telegram_agent" / "mcp_servers.json"
        self.servers: Dict[str, Dict] = self._load_default_servers()
        self._load_custom_servers()
    
    def _load_default_servers(self) -> Dict[str, Dict]:
        """Load default MCP server configurations"""
        return {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(Path.home())],
                "description": "Local filesystem access",
                "auth_required": False,
                "category": "storage"
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "description": "GitHub repositories and issues",
                "auth_required": True,
                "env_vars": ["GITHUB_TOKEN"],
                "category": "development"
            },
            "gdrive": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-gdrive"],
                "description": "Google Drive files and folders",
                "auth_required": True,
                "env_vars": ["GDRIVE_CREDENTIALS_PATH"],
                "category": "storage"
            },
            "gmail": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-gmail"],
                "description": "Gmail email management",
                "auth_required": True,
                "env_vars": ["GMAIL_CREDENTIALS_PATH"],
                "category": "communication"
            },
            "slack": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-slack"],
                "description": "Slack workspace integration",
                "auth_required": True,
                "env_vars": ["SLACK_TOKEN"],
                "category": "communication"
            },
            "notion": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-notion"],
                "description": "Notion workspace integration",
                "auth_required": True,
                "env_vars": ["NOTION_TOKEN"],
                "category": "productivity"
            },
            "calendar": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-google-calendar"],
                "description": "Google Calendar integration",
                "auth_required": True,
                "env_vars": ["CALENDAR_CREDENTIALS_PATH"],
                "category": "productivity"
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres"],
                "description": "PostgreSQL database",
                "auth_required": True,
                "env_vars": ["POSTGRES_CONNECTION_STRING"],
                "category": "database"
            },
            "mysql": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-mysql"],
                "description": "MySQL database",
                "auth_required": True,
                "env_vars": ["MYSQL_CONNECTION_STRING"],
                "category": "database"
            },
            "mongodb": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-mongodb"],
                "description": "MongoDB database",
                "auth_required": True,
                "env_vars": ["MONGODB_CONNECTION_STRING"],
                "category": "database"
            }
        }
    
    def _load_custom_servers(self):
        """Load custom server configurations from file"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r') as f:
                custom_servers = json.load(f)
            self.servers.update(custom_servers)
            logger.info(f"Loaded {len(custom_servers)} custom MCP servers")
        except Exception as e:
            logger.error(f"Failed to load custom servers: {e}")
    
    def add_server(self, name: str, config: Dict) -> bool:
        """Add a custom server"""
        if name in self.servers:
            logger.warning(f"Server {name} already exists, overwriting")
        
        self.servers[name] = config
        return self._save_custom_servers()
    
    def remove_server(self, name: str) -> bool:
        """Remove a custom server"""
        if name not in self.servers:
            return False
        
        del self.servers[name]
        return self._save_custom_servers()
    
    def get_server(self, name: str) -> Optional[Dict]:
        """Get server configuration"""
        return self.servers.get(name)
    
    def list_servers(self, category: Optional[str] = None) -> List[Dict]:
        """List all servers, optionally filtered by category"""
        servers = []
        for name, config in self.servers.items():
            if category and config.get("category") != category:
                continue
            servers.append({
                "name": name,
                **config
            })
        return servers
    
    def list_categories(self) -> List[str]:
        """List all server categories"""
        categories = set()
        for config in self.servers.values():
            if "category" in config:
                categories.add(config["category"])
        return sorted(categories)
    
    def _save_custom_servers(self) -> bool:
        """Save custom servers to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.servers, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save custom servers: {e}")
            return False


# Singleton instance
_registry = None

def get_registry() -> MCPServerRegistry:
    """Get the MCP server registry singleton"""
    global _registry
    if _registry is None:
        _registry = MCPServerRegistry()
    return _registry
