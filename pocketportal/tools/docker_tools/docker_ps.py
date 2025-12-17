"""
Docker PS Tool - List containers
"""

import asyncio
import logging
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class DockerPSTool(BaseTool):
    """List Docker containers"""
    
    def __init__(self):
        super().__init__()
        self.client = None
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="docker_ps",
            description="List Docker containers",
            category=ToolCategory.SYSTEM,
            parameters={
                "all": {
                    "type": "boolean",
                    "required": False,
                    "description": "Show all containers (default: running only)"
                },
                "filters": {
                    "type": "object",
                    "required": False,
                    "description": "Filter containers"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List containers"""
        
        if not DOCKER_AVAILABLE:
            return self._error_response("Docker SDK not installed. Run: pip install docker")
        
        try:
            if not self.client:
                self.client = docker.from_env()
            
            all_containers = parameters.get("all", False)
            filters = parameters.get("filters", {})
            
            containers = self.client.containers.list(all=all_containers, filters=filters)
            
            result = []
            for container in containers:
                result.append({
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "status": container.status,
                    "ports": container.ports
                })
            
            return self._success_response(
                result=result,
                metadata={"count": len(result)}
            )
        
        except Exception as e:
            return self._error_response(f"Docker PS failed: {str(e)}")
