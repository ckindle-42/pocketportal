"""
Git Clone Tool - Clone repositories
"""

import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

from pocketportal.core.interfaces.tool import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)

try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitCloneTool(BaseTool):
    """Clone Git repositories"""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_clone",
            description="Clone a Git repository to local machine",
            category=ToolCategory.DEVELOPMENT,
            requires_confirmation=True,
            parameters={
                "url": {
                    "type": "string",
                    "required": True,
                    "description": "Repository URL (HTTPS or SSH)"
                },
                "destination": {
                    "type": "string",
                    "required": False,
                    "description": "Destination directory (default: repo name)"
                },
                "branch": {
                    "type": "string",
                    "required": False,
                    "description": "Branch to clone (default: default branch)"
                },
                "depth": {
                    "type": "integer",
                    "required": False,
                    "description": "Clone depth for shallow clone"
                }
            }
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git clone"""
        
        if not GIT_AVAILABLE:
            return self._error_response("GitPython not installed. Run: pip install GitPython")
        
        url = parameters.get("url")
        destination = parameters.get("destination")
        branch = parameters.get("branch")
        depth = parameters.get("depth")
        
        try:
            # Prepare clone arguments
            kwargs = {}
            if branch:
                kwargs["branch"] = branch
            if depth:
                kwargs["depth"] = depth
            
            # Clone repository
            logger.info(f"Cloning {url}")
            repo = Repo.clone_from(url, destination or None, **kwargs)
            
            return self._success_response(
                result=f"Successfully cloned to {repo.working_dir}",
                metadata={
                    "url": url,
                    "path": str(repo.working_dir),
                    "branch": repo.active_branch.name,
                    "commit": repo.head.commit.hexsha[:8]
                }
            )
        
        except GitCommandError as e:
            return self._error_response(f"Git clone failed: {e}")
        except Exception as e:
            return self._error_response(f"Clone failed: {str(e)}")
