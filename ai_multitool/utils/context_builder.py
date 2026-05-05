"""Smart context builder for code analysis."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ai_multitool.parsers.code_parser import CodeParser, CodeStructure, get_parser
from ai_multitool.utils.git_utils import GitHelper, GitContext, get_git_helper
from ai_multitool.utils.file_utils import is_code_file


@dataclass
class AnalysisContext:
    """Complete context for code analysis."""
    file_path: str
    code_structure: Optional[CodeStructure]
    git_context: Optional[GitContext]
    related_files: List[str]
    dependencies: List[str]
    file_stats: Dict[str, int]
    context_string: str


class SmartContextBuilder:
    """Build intelligent context for code analysis."""
    
    def __init__(self):
        """Initialize the context builder."""
        self.parser = get_parser()
        self.git_helper = get_git_helper()
    
    def build_context(
        self,
        path: str,
        include_git: bool = True,
        include_related: bool = True,
        max_related: int = 5,
        max_context_length: int = 8000
    ) -> AnalysisContext:
        """Build comprehensive analysis context for a file or directory."""
        path_obj = Path(path)
        
        if not path_obj.exists():
            return AnalysisContext(
                file_path=path,
                code_structure=None,
                git_context=None,
                related_files=[],
                dependencies=[],
                file_stats={},
                context_string=f"Error: Path not found: {path}"
            )
        
        # Get code structure
        if path_obj.is_file():
            code_structure = self.parser.parse_file(path)
            related_files = self._find_related_files(path, max_related) if include_related else []
            dependencies = self._extract_dependencies(path)
        else:
            structures = self.parser.parse_directory(path, max_files=50)
            code_structure = None  # Directory doesn't have single structure
            related_files = [s.file_path for s in structures[:max_related]] if include_related else []
            dependencies = []
        
        # Get git context
        git_context = self.git_helper.get_context(str(path_obj.absolute())) if include_git else None
        
        # Get file stats
        file_stats = self._get_file_stats(path)
        
        # Build context string
        context_string = self._build_context_string(
            path_obj,
            code_structure,
            git_context,
            related_files,
            dependencies,
            file_stats,
            max_context_length
        )
        
        return AnalysisContext(
            file_path=str(path_obj.absolute()),
            code_structure=code_structure,
            git_context=git_context,
            related_files=related_files,
            dependencies=dependencies,
            file_stats=file_stats,
            context_string=context_string
        )
    
    def _find_related_files(self, file_path: str, max_files: int = 5) -> List[str]:
        """Find related files based on imports and directory structure."""
        related = []
        path_obj = Path(file_path)
        directory = path_obj.parent
        
        # Get files in same directory
        try:
            for file in directory.iterdir():
                if file.is_file() and is_code_file(str(file)) and file != path_obj:
                    related.append(str(file))
                    if len(related) >= max_files:
                        break
        except Exception:
            pass
        
        return related
    
    def _extract_dependencies(self, file_path: str) -> List[str]:
        """Extract import/dependency information from a file."""
        dependencies = []
        
        try:
            structure = self.parser.parse_file(file_path)
            if structure:
                dependencies = structure.imports
        except Exception:
            pass
        
        return dependencies
    
    def _get_file_stats(self, path: str) -> Dict[str, int]:
        """Get statistics about the file or directory."""
        path_obj = Path(path)
        stats = {}
        
        try:
            if path_obj.is_file():
                content = path_obj.read_text(encoding='utf-8', errors='ignore')
                stats = {
                    'lines': len(content.splitlines()),
                    'chars': len(content),
                    'size_bytes': path_obj.stat().st_size,
                }
            elif path_obj.is_dir():
                total_lines = 0
                total_chars = 0
                file_count = 0
                
                for file in path_obj.rglob('*'):
                    if file.is_file() and is_code_file(str(file)):
                        try:
                            content = file.read_text(encoding='utf-8', errors='ignore')
                            total_lines += len(content.splitlines())
                            total_chars += len(content)
                            file_count += 1
                        except Exception:
                            pass
                
                stats = {
                    'files': file_count,
                    'total_lines': total_lines,
                    'total_chars': total_chars,
                }
        except Exception:
            pass
        
        return stats
    
    def _build_context_string(
        self,
        path_obj: Path,
        code_structure: Optional[CodeStructure],
        git_context: Optional[GitContext],
        related_files: List[str],
        dependencies: List[str],
        file_stats: Dict[str, int],
        max_length: int
    ) -> str:
        """Build a formatted context string."""
        parts = []
        
        # File/directory info
        if path_obj.is_file():
            parts.append(f"File: {path_obj.name}")
            parts.append(f"Path: {str(path_obj.absolute())}")
        else:
            parts.append(f"Directory: {path_obj.name}")
            parts.append(f"Path: {str(path_obj.absolute())}")
        
        # File stats
        if file_stats:
            parts.append("\nFile Statistics:")
            for key, value in file_stats.items():
                parts.append(f"  {key}: {value}")
        
        # Code structure
        if code_structure:
            parts.append("\nCode Structure:")
            parts.append(f"  Language: {code_structure.language}")
            parts.append(f"  Functions: {len(code_structure.functions)}")
            parts.append(f"  Classes: {len(code_structure.classes)}")
            parts.append(f"  Complexity: {code_structure.complexity_score}")
            
            if code_structure.functions:
                parts.append("\n  Functions:")
                for func in code_structure.functions[:5]:
                    parts.append(f"    - {func['name']}({func['params']})")
                if len(code_structure.functions) > 5:
                    parts.append(f"    ... and {len(code_structure.functions) - 5} more")
            
            if code_structure.classes:
                parts.append("\n  Classes:")
                for cls in code_structure.classes[:5]:
                    parts.append(f"    - {cls['name']}" + 
                                (f" extends {cls['inherits']}" if cls['inherits'] else ''))
                if len(code_structure.classes) > 5:
                    parts.append(f"    ... and {len(code_structure.classes) - 5} more")
        
        # Dependencies
        if dependencies:
            parts.append("\nDependencies/Imports:")
            for dep in dependencies[:10]:
                parts.append(f"  - {dep}")
            if len(dependencies) > 10:
                parts.append(f"  ... and {len(dependencies) - 10} more")
        
        # Related files
        if related_files:
            parts.append("\nRelated Files:")
            for rf in related_files[:5]:
                parts.append(f"  - {Path(rf).name}")
            if len(related_files) > 5:
                parts.append(f"  ... and {len(related_files) - 5} more")
        
        # Git context
        if git_context and git_context.is_repo:
            parts.append("\nGit Context:")
            parts.append(f"  Branch: {git_context.branch}")
            parts.append(f"  Commit: {git_context.commit_hash}")
            parts.append(f"  Status: {git_context.status}")
            
            if git_context.modified_files:
                parts.append(f"  Modified: {', '.join(git_context.modified_files[:5])}")
            
            if git_context.recent_commits:
                parts.append("\n  Recent Commits:")
                for commit in git_context.recent_commits[:3]:
                    parts.append(f"    - {commit['hash']}: {commit['message'][:50]}")
        
        context = "\n".join(parts)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "\n... (context truncated)"
        
        return context
    
    def build_directory_summary(self, directory: str, max_files: int = 20) -> str:
        """Build a summary of a directory's code structure."""
        structures = self.parser.parse_directory(directory, max_files)
        
        if not structures:
            return "No code files found in directory."
        
        # Group by language
        by_language = {}
        for s in structures:
            lang = s.language
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(s)
        
        parts = [f"Directory Summary: {directory}"]
        parts.append(f"Total files: {len(structures)}")
        
        for lang, lang_structures in sorted(by_language.items()):
            total_funcs = sum(len(s.functions) for s in lang_structures)
            total_classes = sum(len(s.classes) for s in lang_structures)
            parts.append(f"\n{lang}:")
            parts.append(f"  Files: {len(lang_structures)}")
            parts.append(f"  Functions: {total_funcs}")
            parts.append(f"  Classes: {total_classes}")
        
        return "\n".join(parts)


# Singleton instance
_context_builder_instance: Optional[SmartContextBuilder] = None


def get_context_builder() -> SmartContextBuilder:
    """Get the singleton context builder instance."""
    global _context_builder_instance
    if _context_builder_instance is None:
        _context_builder_instance = SmartContextBuilder()
    return _context_builder_instance
