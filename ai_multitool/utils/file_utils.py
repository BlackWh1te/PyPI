"""File reading utilities"""

from pathlib import Path
from typing import List, Optional
import os


def read_file(file_path: str) -> str:
    """Read file content"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    return path.read_text(encoding="utf-8")


def read_directory(directory: str, pattern: str = "*") -> List[str]:
    """Read all files in a directory matching pattern"""
    path = Path(directory)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    files = []
    for file_path in path.rglob(pattern):
        if file_path.is_file():
            files.append(str(file_path))
    return files


def get_file_info(file_path: str) -> dict:
    """Get file information"""
    path = Path(file_path)
    stat = path.stat()

    return {
        "name": path.name,
        "size": stat.st_size,
        "extension": path.suffix,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "absolute_path": str(path.absolute()),
    }


def is_code_file(file_path: str) -> bool:
    """Check if file is a code file based on extension"""
    code_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".rb", ".php",
        ".swift", ".kt", ".scala", ".sh",
        ".sql", ".json", ".yaml", ".yml", ".toml",
        ".xml", ".html", ".css", ".scss", ".sass",
    }
    return Path(file_path).suffix.lower() in code_extensions
