"""
System Stats Tool - Monitor system resources
"""

import asyncio
import logging
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base_tool import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)

import psutil


class SystemStatsTool(BaseTool):
    """Monitor system resources"""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="system_stats",
            description="Get system resource usage (CPU, RAM, disk)",
            category=ToolCategory.SYSTEM,
            parameters={
                "detailed": {
                    "type": "boolean",
                    "required": False,
                    "description": "Include detailed per-core/disk stats"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get system stats"""
        
        detailed = parameters.get("detailed", False)
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            mem = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            result = {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "percent": mem.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent
                }
            }
            
            if detailed:
                result["cpu"]["per_core"] = psutil.cpu_percent(interval=1, percpu=True)
                result["disk"]["partitions"] = [
                    {
                        "device": p.device,
                        "mountpoint": p.mountpoint,
                        "fstype": p.fstype
                    }
                    for p in psutil.disk_partitions()
                ]
            
            return self._success_response(result=result)
        
        except Exception as e:
            return self._error_response(f"Failed to get system stats: {str(e)}")
