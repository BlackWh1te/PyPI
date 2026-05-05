"""AI-powered commit message generation."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...utils.git_utils import GitHelper


class AdvancedCommitGenerator(AdvancedTool):
    """AI-powered commit message generation.
    
    Generates conventional commit messages based on:
    - Git diff
    - Staged changes
    - Branch name
    - Commit history
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.git_helper = GitHelper()
    
    
        """Get the tool definition for commit gen.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "generate_commit_message",
            "description": "Generate conventional commit messages from changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "default": "."},
                    "style": {"type": "string", "enum": ["conventional", "concise", "detailed"], "default": "conventional"},
                    "include_scope": {"type": "boolean", "default": True}
                },
                "required": []
            }
        }
    
    async def execute(self, repo_path: str = ".", style: str = "conventional",
                     include_scope: bool = True, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get git diff
            diff = self.git_helper.get_diff(repo_path)
            if not diff:
                return ToolResult(success=False, errors=["No changes to commit"])
            
            # Get branch info
            branch = self.git_helper.get_branch(repo_path)
            
            # Get recent commits for context
            recent_commits = self.git_helper.get_recent_commits(repo_path, limit=5)
            
            # Build prompt
            prompt = self._build_commit_prompt(diff, branch, recent_commits, style, include_scope)
            
            # Generate commit message
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            commit_message = response.content.strip()
            
            # Parse into components
            components = self._parse_commit_message(commit_message)
            
            return ToolResult(
                success=True,
                data={
                    "commit_message": commit_message,
                    "components": components,
                    "branch": branch,
                    "style": style
                },
                suggestions=["Review commit message before using"],
                confidence=0.85,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _build_commit_prompt(self, diff: str, branch: str, recent_commits: List[Dict],
                            style: str, include_scope: bool) -> str:
        commits_context = "\n".join([f"- {c.get('message', '')}" for c in recent_commits])
        
        return f"""Generate a commit message for these changes:

Branch: {branch}

Recent commits:
{commits_context}

Changes (git diff):
{diff}

Requirements:
- Style: {style}
- Include scope: {include_scope}
- Follow conventional commit format if conventional style
- Be clear and concise
- Focus on WHAT and WHY, not HOW

Provide just the commit message."""
    
    def _parse_commit_message(self, message: str) -> Dict[str, str]:
        # Parse conventional commit format
        parts = message.split(":", 1)
        if len(parts) == 2:
            type_scope = parts[0].strip()
            if "(" in type_scope:
                type_part, scope_part = type_scope.split(")", 1)
                commit_type = type_part.replace("(", "")
                scope = scope_part.strip()
            else:
                commit_type = type_scope
                scope = ""
            description = parts[1].strip()
            
            return {
                "type": commit_type,
                "scope": scope,
                "description": description
            }
        return {"raw": message}
