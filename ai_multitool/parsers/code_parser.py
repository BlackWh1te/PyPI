"""Code parsing utilities using tree-sitter."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


@dataclass
class CodeStructure:
    """Represents the structure of parsed code."""
    file_path: str
    language: str
    functions: List[Dict]
    classes: List[Dict]
    imports: List[str]
    docstrings: List[str]
    complexity_score: int


class CodeParser:
    """Parse code files using tree-sitter for structure analysis."""
    
    # Language mappings for tree-sitter
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.jsx': 'jsx',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
    }
    
    def __init__(self):
        """Initialize the code parser."""
        self.parser = None
        self.languages: Dict[str, Language] = {}
        self._init_parser()
    
    def _init_parser(self):
        """Initialize tree-sitter parser with available languages."""
        if not TREE_SITTER_AVAILABLE:
            return
        
        try:
            self.parser = Parser()
            # Try to load languages from common locations
            self._load_languages()
        except Exception as e:
            print(f"Warning: Failed to initialize tree-sitter parser: {e}")
    
    def _load_languages(self):
        """Load tree-sitter language grammars."""
        # Common locations for tree-sitter language libraries
        search_paths = [
            os.path.expanduser('~/.local/share/tree-sitter/parsers'),
            '/usr/local/lib/tree-sitter',
            os.path.join(os.path.dirname(__file__), '..', '..', 'tree-sitter-languages'),
        ]
        
        for lang_name, file_ext in self.LANGUAGE_MAP.items():
            # For now, we'll use a simpler approach with tree-sitter-languages package
            # if available
            pass
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_MAP.get(ext)
    
    def parse_file(self, file_path: str) -> Optional[CodeStructure]:
        """Parse a code file and extract its structure."""
        if not TREE_SITTER_AVAILABLE:
            return self._fallback_parse(file_path)
        
        language = self.detect_language(file_path)
        if not language:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            
            # For now, use regex-based parsing as fallback
            # Full tree-sitter integration requires language-specific grammars
            return self._parse_with_regex(content, language, file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _fallback_parse(self, file_path: str) -> Optional[CodeStructure]:
        """Fallback parsing using regex when tree-sitter is not available."""
        language = self.detect_language(file_path)
        if not language:
            return None
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            return self._parse_with_regex(content, language, file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_with_regex(self, content: str, language: str, file_path: str) -> CodeStructure:
        """Parse code using regex patterns (fallback method)."""
        import re
        
        functions = []
        classes = []
        imports = []
        docstrings = []
        
        if language == 'python':
            # Extract functions
            func_pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(func_pattern, content):
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': content[:match.start()].count('\n') + 1
                })
            
            # Extract classes
            class_pattern = r'class\s+(\w+)\s*(?:\(([^)]*)\))?'
            for match in re.finditer(class_pattern, content):
                classes.append({
                    'name': match.group(1),
                    'inherits': match.group(2) or '',
                    'line': content[:match.start()].count('\n') + 1
                })
            
            # Extract imports
            import_patterns = [
                r'import\s+([\w\s,]+)',
                r'from\s+(\w+)\s+import\s+([\w\s,]+)'
            ]
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    imports.append(match.group(0))
            
            # Extract docstrings
            docstring_pattern = r'"""([^"]|"[^"]|""[^"])*"""'
            for match in re.finditer(docstring_pattern, content, re.DOTALL):
                docstrings.append(match.group(0))
        
        elif language in ['javascript', 'typescript', 'jsx', 'tsx']:
            # Extract functions
            func_pattern = r'(?:function\s+(\w+)\s*\(([^)]*)\)|const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>)'
            for match in re.finditer(func_pattern, content):
                name = match.group(1) or match.group(3)
                params = match.group(2) or match.group(4)
                if name:
                    functions.append({
                        'name': name,
                        'params': params or '',
                        'line': content[:match.start()].count('\n') + 1
                    })
            
            # Extract classes
            class_pattern = r'class\s+(\w+)\s*(?:extends\s+(\w+))?'
            for match in re.finditer(class_pattern, content):
                classes.append({
                    'name': match.group(1),
                    'inherits': match.group(2) or '',
                    'line': content[:match.start()].count('\n') + 1
                })
            
            # Extract imports
            import_patterns = [
                r'import\s+.*?from\s+[\'"][^\'"]+[\'"]',
                r'require\([\'"][^\'"]+[\'"]\)'
            ]
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    imports.append(match.group(0))
        
        # Calculate simple complexity score
        complexity = len(functions) + len(classes) * 2 + len(imports)
        
        return CodeStructure(
            file_path=file_path,
            language=language,
            functions=functions,
            classes=classes,
            imports=imports,
            docstrings=docstrings,
            complexity_score=complexity
        )
    
    def parse_directory(self, directory: str, max_files: int = 50) -> List[CodeStructure]:
        """Parse all code files in a directory."""
        structures = []
        directory = Path(directory)
        
        if not directory.is_dir():
            return structures
        
        code_extensions = set(self.LANGUAGE_MAP.keys())
        
        for file_path in directory.rglob('*'):
            if len(structures) >= max_files:
                break
            
            if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                # Skip common non-code directories
                if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', 'env']
                       for part in file_path.parts):
                    continue
                
                structure = self.parse_file(str(file_path))
                if structure:
                    structures.append(structure)
        
        return structures
    
    def get_summary(self, structures: List[CodeStructure]) -> str:
        """Generate a summary of parsed code structures."""
        if not structures:
            return "No code files found."
        
        total_functions = sum(len(s.functions) for s in structures)
        total_classes = sum(len(s.classes) for s in structures)
        languages = {}
        
        for s in structures:
            languages[s.language] = languages.get(s.language, 0) + 1
        
        summary = [
            f"Analyzed {len(structures)} code files",
            f"Languages: {', '.join(f'{k} ({v})' for k, v in sorted(languages.items()))}",
            f"Total functions: {total_functions}",
            f"Total classes: {total_classes}",
            f"Average complexity: {sum(s.complexity_score for s in structures) // len(structures):.1f}",
        ]
        
        return '\n'.join(summary)
    
    def structure_to_context(self, structure: CodeStructure, max_length: int = 5000) -> str:
        """Convert code structure to a context string for AI analysis."""
        lines = [
            f"File: {structure.file_path}",
            f"Language: {structure.language}",
            f"Complexity: {structure.complexity_score}",
        ]
        
        if structure.functions:
            lines.append("\nFunctions:")
            for func in structure.functions[:10]:  # Limit to first 10
                lines.append(f"  - {func['name']}({func['params']}) at line {func['line']}")
            if len(structure.functions) > 10:
                lines.append(f"  ... and {len(structure.functions) - 10} more")
        
        if structure.classes:
            lines.append("\nClasses:")
            for cls in structure.classes[:10]:
                lines.append(f"  - {cls['name']}" + 
                            (f" extends {cls['inherits']}" if cls['inherits'] else '') +
                            f" at line {cls['line']}")
            if len(structure.classes) > 10:
                lines.append(f"  ... and {len(structure.classes) - 10} more")
        
        if structure.imports:
            lines.append("\nImports:")
            for imp in structure.imports[:10]:
                lines.append(f"  - {imp}")
            if len(structure.imports) > 10:
                lines.append(f"  ... and {len(structure.imports) - 10} more")
        
        result = '\n'.join(lines)
        
        # Truncate if too long
        if len(result) > max_length:
            result = result[:max_length] + "\n... (truncated)"
        
        return result


# Singleton instance
_parser_instance: Optional[CodeParser] = None


def get_parser() -> CodeParser:
    """Get the singleton code parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = CodeParser()
    return _parser_instance
