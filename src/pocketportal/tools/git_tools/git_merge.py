"""
Git Merge Tool - Merge branches
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


class GitMergeTool(BaseTool):
    """Merge Git branches"""

    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_merge",
            description="Merge one Git branch into another",
            category=ToolCategory.DEVELOPMENT,
            requires_confirmation=True,  # Merges modify history
            parameters={
                "repo_path": {
                    "type": "string",
                    "required": False,
                    "description": "Path to repository (default: current directory)"
                },
                "branch": {
                    "type": "string",
                    "required": True,
                    "description": "Branch to merge into current branch"
                },
                "no_ff": {
                    "type": "boolean",
                    "required": False,
                    "description": "Create merge commit even if fast-forward possible"
                },
                "message": {
                    "type": "string",
                    "required": False,
                    "description": "Custom merge commit message"
                }
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute git merge"""

        if not GIT_AVAILABLE:
            return self._error_response("GitPython not installed. Run: pip install GitPython")

        repo_path = parameters.get("repo_path", ".")
        branch_name = parameters.get("branch")
        no_ff = parameters.get("no_ff", False)
        message = parameters.get("message")

        if not branch_name:
            return self._error_response("Branch name is required")

        try:
            # Open repository
            repo = Repo(repo_path)

            if repo.bare:
                return self._error_response("Repository is bare")

            # Check for uncommitted changes
            if repo.is_dirty():
                return self._error_response(
                    "Working tree has uncommitted changes. Commit or stash them first."
                )

            # Check if branch exists
            if branch_name not in [b.name for b in repo.branches]:
                return self._error_response(f"Branch '{branch_name}' not found")

            # Get current branch
            current_branch = repo.active_branch.name
            current_commit = repo.head.commit.hexsha[:8]

            # Build merge arguments
            merge_args = [branch_name]
            if no_ff:
                merge_args.extend(['--no-ff'])
            if message:
                merge_args.extend(['-m', message])

            # Execute merge
            logger.info(f"Merging {branch_name} into {current_branch}")

            try:
                repo.git.merge(*merge_args)
                new_commit = repo.head.commit.hexsha[:8]

                # Check if it was a fast-forward
                was_ff = current_commit != new_commit and not no_ff

                return self._success_response(
                    result=f"Successfully merged {branch_name} into {current_branch}",
                    metadata={
                        "current_branch": current_branch,
                        "merged_branch": branch_name,
                        "old_commit": current_commit,
                        "new_commit": new_commit,
                        "fast_forward": was_ff
                    }
                )
            except GitCommandError as e:
                if "CONFLICT" in str(e):
                    return self._error_response(
                        f"Merge conflict detected. Resolve conflicts and commit manually.\n{str(e)}"
                    )
                raise

        except InvalidGitRepositoryError:
            return self._error_response(f"Not a git repository: {repo_path}")
        except GitCommandError as e:
            return self._error_response(f"Git command failed: {e}")
        except Exception as e:
            return self._error_response(f"Merge failed: {str(e)}")
