"""Git utilities for repository context."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ai_multitool.core.exceptions import GitError, ValidationError

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


@dataclass
class GitContext:
    """Represents git repository context."""
    is_repo: bool
    branch: Optional[str]
    commit_hash: Optional[str]
    commit_message: Optional[str]
    author: Optional[str]
    modified_files: List[str]
    untracked_files: List[str]
    recent_commits: List[Dict]
    status: str


class GitHelper:
    """Helper class for git operations."""
    
    def __init__(self, repo_path: str = None):
        """Initialize git helper for a repository."""
        if not GIT_AVAILABLE:
            raise GitError(
                "Git library not installed",
                suggestion="Install gitpython: pip install gitpython"
            )
        
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        
        try:
            if not os.path.exists(self.repo_path):
                raise GitError(
                    f"Repository path does not exist: {self.repo_path}",
                    suggestion="Check if the path is correct"
                )
            
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            # Not a git repo - this is OK, just set repo to None
            self.repo = None
        except GitError:
            raise
        except Exception as e:
            raise GitError(
                f"Failed to initialize git repository",
                details={"error_type": type(e).__name__, "error": str(e), "path": self.repo_path}
            )
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        return self.repo is not None
    
    def get_branch(self) -> Optional[str]:
        """Get current branch name."""
        if not self.repo:
            return None
        try:
            return self.repo.active_branch.name
        except git.NoSuchPathError:
            return None
        except git.InvalidGitRepositoryError:
            return None
        except Exception:
            return None
    
    def get_commit_info(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get current commit hash, message, and author."""
        if not self.repo:
            return None, None, None
        try:
            commit = self.repo.head.commit
            return (
                commit.hexsha[:8],  # Short hash
                commit.message.strip(),
                f"{commit.author.name} <{commit.author.email}>"
            )
        except (git.NoSuchPathError, git.InvalidGitRepositoryError, ValueError):
            return None, None, None
        except Exception:
            return None, None, None
    
    def get_status(self) -> Tuple[List[str], List[str], str]:
        """Get modified files, untracked files, and status string."""
        if not self.repo:
            return [], [], "Not a git repository"
        
        try:
            modified = [item.a_path for item in self.repo.index.diff(None)]
            untracked = self.repo.untracked_files
            
            # Build status string
            status_parts = []
            if modified:
                status_parts.append(f"{len(modified)} modified")
            if untracked:
                status_parts.append(f"{len(untracked)} untracked")
            if not status_parts:
                status_parts.append("Clean")
            
            status = ", ".join(status_parts)
            return modified, untracked, status
        except (git.NoSuchPathError, git.InvalidGitRepositoryError):
            return [], [], "Not a git repository"
        except Exception:
            return [], [], "Error getting status"
    
    def get_recent_commits(self, limit: int = 5) -> List[Dict]:
        """Get recent commit history."""
        if not self.repo:
            return []
        
        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100", field="limit")
        
        commits = []
        try:
            for commit in list(self.repo.iter_commits(max_count=limit)):
                commits.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': f"{commit.author.name}",
                    'date': commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                })
        except (git.NoSuchPathError, git.InvalidGitRepositoryError):
            return []
        except Exception:
            pass
        
        return commits
    
    def get_file_history(self, file_path: str, limit: int = 5) -> List[Dict]:
        """Get commit history for a specific file."""
        if not self.repo:
            return []
        
        if not file_path or not file_path.strip():
            raise ValidationError("File path cannot be empty", field="file_path")
        
        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100", field="limit")
        
        commits = []
        try:
            for commit in list(self.repo.iter_commits(paths=file_path, max_count=limit)):
                commits.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': f"{commit.author.name}",
                    'date': commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                })
        except (git.NoSuchPathError, git.InvalidGitRepositoryError):
            return []
        except Exception:
            pass
        
        return commits
    
    def get_diff(self, file_path: str = None) -> str:
        """Get git diff for working directory or specific file."""
        if not self.repo:
            return ""
        
        try:
            if file_path:
                diff = self.repo.index.diff(None, paths=[file_path])
            else:
                diff = self.repo.index.diff(None)
            
            diff_text = ""
            for item in diff:
                diff_text += f"\n{item.a_path}:\n"
                diff_text += item.diff.decode('utf-8', errors='ignore')
            
            return diff_text
        except (git.NoSuchPathError, git.InvalidGitRepositoryError):
            return ""
        except Exception:
            return ""
    
    def get_context(self, file_path: str = None) -> GitContext:
        """Get complete git context for analysis."""
        is_repo = self.is_git_repo()
        
        if not is_repo:
            return GitContext(
                is_repo=False,
                branch=None,
                commit_hash=None,
                commit_message=None,
                author=None,
                modified_files=[],
                untracked_files=[],
                recent_commits=[],
                status="Not a git repository"
            )
        
        branch = self.get_branch()
        commit_hash, commit_message, author = self.get_commit_info()
        modified, untracked, status = self.get_status()
        
        if file_path:
            recent_commits = self.get_file_history(file_path)
        else:
            recent_commits = self.get_recent_commits()
        
        return GitContext(
            is_repo=True,
            branch=branch,
            commit_hash=commit_hash,
            commit_message=commit_message,
            author=author,
            modified_files=modified,
            untracked_files=untracked,
            recent_commits=recent_commits,
            status=status
        )
    
    def context_to_string(self, context: GitContext, max_length: int = 3000) -> str:
        """Convert git context to a formatted string."""
        if not context.is_repo:
            return "Git context: Not a git repository"
        
        lines = [
            "Git Repository Context:",
            f"  Branch: {context.branch}",
            f"  Current commit: {context.commit_hash}",
            f"  Commit message: {context.commit_message}",
            f"  Author: {context.author}",
            f"  Status: {context.status}",
        ]
        
        if context.modified_files:
            lines.append(f"  Modified files: {', '.join(context.modified_files[:10])}")
            if len(context.modified_files) > 10:
                lines.append(f"    ... and {len(context.modified_files) - 10} more")
        
        if context.untracked_files:
            lines.append(f"  Untracked files: {', '.join(context.untracked_files[:10])}")
            if len(context.untracked_files) > 10:
                lines.append(f"    ... and {len(context.untracked_files) - 10} more")
        
        if context.recent_commits:
            lines.append("\n  Recent commits:")
            for commit in context.recent_commits[:5]:
                lines.append(f"    - {commit['hash']}: {commit['message'][:50]}")
        
        result = "\n".join(lines)
        
        # Truncate if too long
        if len(result) > max_length:
            result = result[:max_length] + "\n... (truncated)"
        
        return result


def get_git_helper(repo_path: str = None) -> Optional[GitHelper]:
    """Get a git helper instance. Returns None if git is not available."""
    if not GIT_AVAILABLE:
        return None
    
    try:
        return GitHelper(repo_path)
    except GitError:
        # Return None if not a git repo or other git error
        return None
