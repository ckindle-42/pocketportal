"""
Git Commit Tool - Commit changes
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
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitCommitTool(BaseTool):
    """Commit changes to Git repository"""

    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_commit",
            description="Commit staged changes to Git repository",
            category=ToolCategory.DEVELOPMENT,
            requires_confirmation=True,  # Commits modify history
            parameters={
                "repo_path": {
                    "type": "string",
                    "required": False,
                    "description": "Path to repository (default: current directory)"
                },
                "message": {
                    "type": "string",
                    "required": True,
                    "description": "Commit message"
                },
                "add_all": {
                    "type": "boolean",
                    "required": False,
                    "description": "Add all modified files before committing (default: False)"
                },
                "files": {
                    "type": "list",
                    "required": False,
                    "description": "Specific files to add before committing"
                }
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git commit"""

        if not GIT_AVAILABLE:
            return self._error_response("GitPython not installed. Run: pip install GitPython")

        repo_path = parameters.get("repo_path", ".")
        message = parameters.get("message")
        add_all = parameters.get("add_all", False)
        files = parameters.get("files", [])

        if not message:
            return self._error_response("Commit message is required")

        try:
            # Open repository
            repo = Repo(repo_path)

            if repo.bare:
                return self._error_response("Repository is bare")

            # Add files if requested
            if add_all:
                repo.git.add(A=True)
            elif files:
                repo.index.add(files)

            # Check if there's anything to commit
            if not repo.index.diff("HEAD") and not repo.untracked_files:
                return self._error_response("Nothing to commit (working tree clean)")

            # Create commit
            commit = repo.index.commit(message)

            return self._success_response(
                result=f"Created commit {commit.hexsha[:8]}: {message}",
                metadata={
                    "commit": commit.hexsha[:8],
                    "message": message,
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "files_changed": len(commit.stats.files)
                }
            )

        except InvalidGitRepositoryError:
            return self._error_response(f"Not a git repository: {repo_path}")
        except GitCommandError as e:
            return self._error_response(f"Git command failed: {e}")
        except Exception as e:
            return self._error_response(f"Commit failed: {str(e)}")
