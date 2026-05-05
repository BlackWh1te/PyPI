"""Git blame analysis with AI insights."""

import time
from typing import Dict, Any, List, Optional
from ..base import AdvancedTool, ToolResult, ToolStatus
from ...core.models import Message, MessageRole
from ...utils.git_utils import GitHelper


class AdvancedBlameAnalyzer(AdvancedTool):
    """Git blame analysis with AI insights.
    
    Analyzes:
    - Code authorship
    - Contribution patterns
    - Code churn
    - Team velocity
    - Technical debt by author
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.git_helper = GitHelper()
    
    
        """Get the tool definition for blame analyzer.

Returns:
    Tool definition dictionary with name, description, and parameters schema.
    The definition follows the standard tool registration format for
    integration with AI systems and CLI tools.
"""
        
            "name": "analyze_blame",
            "description": "Git blame analysis with AI insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "default": "."},
                    "file_path": {"type": "string"},
                    "analysis_type": {"type": "string", "enum": ["authorship", "churn", "patterns", "all"], "default": "all"}
                },
                "required": []
            }
        }
    
    async def execute(self, repo_path: str = ".", file_path: Optional[str] = None,
                     analysis_type: str = "all", **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Get blame information
            if file_path:
                blame_info = self._get_file_blame(repo_path, file_path)
            else:
                blame_info = self._get_repo_blame(repo_path)
            
            # Get AI insights
            prompt = f"""Analyze this git blame information:

{blame_info}

Analysis type: {analysis_type}

Provide insights in JSON:
{{
    "authorship_summary": {{"author": "lines_contributed"}},
    "code_churn": {{"file": "change_count"}},
    "patterns": ["patterns detected"],
    "recommendations": ["suggestions"],
    "team_velocity": "assessment"
}}"""
            
            response = await self.llm_client.chat([Message(role=MessageRole.USER, content=prompt)])
            
            return ToolResult(
                success=True,
                data={"blame_analysis": response.content, "file": file_path},
                confidence=0.8,
                execution_time_ms=(time.time() - start_time) * 1000,
                tokens_used=response.tokens_used
            )
        except Exception as e:
            return ToolResult(success=False, errors=[str(e)], execution_time_ms=(time.time() - start_time) * 1000)
    
    def _get_file_blame(self, repo_path: str, file_path: str) -> str:
        try:
            import git
            repo = git.Repo(repo_path)
            blame = repo.blame(repo.head, file_path)
            return str(blame)
        except (ImportError, ValueError, git.InvalidGitRepositoryError, git.NoSuchPathError):
            return "Blame information not available"
    
    def _get_repo_blame(self, repo_path: str) -> str:
        commits = self.git_helper.get_recent_commits(repo_path, limit=50)
        return str(commits)
