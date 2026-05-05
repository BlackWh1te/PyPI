"""File reading utilities"""

from pathlib import Path
from typing import List, Optional
import os

from ai_multitool.core.exceptions import (
    FileNotFoundError as CustomFileNotFoundError,
    FileOperationError,
    PermissionError as CustomPermissionError,
    ValidationError,
)
from ai_multitool.utils.validation import is_empty_string


def read_file(file_path: str, max_size: int = 10_000_000) -> str:
    """Read file content with error handling"""
    if is_empty_string(file_path):
        raise ValidationError("File path cannot be empty", field="file_path")
    
    path = Path(file_path)
    
    try:
        if not path.exists():
            raise CustomFileNotFoundError(file_path, suggestion="Check if the file path is correct")
        
        if not path.is_file():
            raise FileOperationError(f"Not a file: {file_path}", file_path, suggestion="Provide a valid file path")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > max_size:
            raise FileOperationError(
                f"File too large ({file_size / 1024 / 1024:.1f}MB)",
                file_path,
                suggestion=f"File exceeds maximum size of {max_size / 1024 / 1024:.1f}MB"
            )
        
        # Try to read with encoding fallback
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding="latin-1")
            except Exception as e:
                raise FileOperationError(
                    f"Failed to read file with encoding",
                    file_path,
                    suggestion="Ensure the file is a text file or check its encoding"
                )
        except PermissionError as e:
            raise CustomPermissionError(file_path)
        except OSError as e:
            raise FileOperationError(
                f"Failed to read file: {e}",
                file_path,
                suggestion="Check file permissions and accessibility"
            )
    
    except (FileOperationError, ValidationError):
        raise
    except Exception as e:
        raise FileOperationError(
            f"Unexpected error reading file",
            file_path,
            details={"error_type": type(e).__name__, "error": str(e)}
        )


def read_directory(directory: str, pattern: str = "*", max_files: int = 1000) -> List[str]:
    """Read all files in a directory matching pattern"""
    if not directory or not directory.strip():
        raise ValidationError("Directory path cannot be empty", field="directory")
    
    path = Path(directory)
    
    try:
        if not path.exists():
            raise CustomFileNotFoundError(directory, suggestion="Check if the directory path is correct")
        
        if not path.is_dir():
            raise FileOperationError(f"Not a directory: {directory}", directory, suggestion="Provide a valid directory path")
        
        files = []
        file_count = 0
        
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                files.append(str(file_path))
                file_count += 1
                
                # Limit to prevent excessive file reads
                if file_count >= max_files:
                    break
        
        return files
    
    except (FileOperationError, ValidationError):
        raise
    except PermissionError as e:
        raise CustomPermissionError(directory)
    except OSError as e:
        raise FileOperationError(
            f"Failed to read directory: {e}",
            directory,
            suggestion="Check directory permissions and accessibility"
        )
    except Exception as e:
        raise FileOperationError(
            f"Unexpected error reading directory",
            directory,
            details={"error_type": type(e).__name__, "error": str(e)}
        )


def get_file_info(file_path: str) -> dict:
    """Get file information with error handling"""
    if is_empty_string(file_path):
        raise ValidationError("File path cannot be empty", field="file_path")
    
    path = Path(file_path)
    
    try:
        if not path.exists():
            raise CustomFileNotFoundError(file_path, suggestion="Check if the file path is correct")
        
        stat = path.stat()

        return {
            "name": path.name,
            "size": stat.st_size,
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "absolute_path": str(path.absolute()),
            "modified_time": stat.st_mtime,
        }
    
    except (FileOperationError, ValidationError):
        raise
    except PermissionError as e:
        raise CustomPermissionError(file_path)
    except OSError as e:
        raise FileOperationError(
            f"Failed to get file info: {e}",
            file_path,
            suggestion="Check file permissions"
        )
    except Exception as e:
        raise FileOperationError(
            f"Unexpected error getting file info",
            file_path,
            details={"error_type": type(e).__name__, "error": str(e)}
        )


def is_code_file(file_path: str) -> bool:
    """Check if file is a code file based on extension"""
    if not file_path:
        return False
    
    code_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".rb", ".php",
        ".swift", ".kt", ".scala", ".sh",
        ".sql", ".json", ".yaml", ".yml", ".toml",
        ".xml", ".html", ".css", ".scss", ".sass",
        ".md", ".rst", ".txt",
    }
    
    try:
        return Path(file_path).suffix.lower() in code_extensions
    except Exception:
        return False


def write_file(file_path: str, content: str, create_dirs: bool = False) -> None:
    """Write content to a file"""
    if is_empty_string(file_path):
        raise ValidationError("File path cannot be empty", field="file_path")
    
    if content is None:
        raise ValidationError("Content cannot be None", field="content")
    
    path = Path(file_path)
    
    try:
        # Create parent directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        path.write_text(content, encoding="utf-8")
    
    except PermissionError as e:
        raise CustomPermissionError(file_path, suggestion="Check write permissions for the file/directory")
    except OSError as e:
        raise FileOperationError(
            f"Failed to write file: {e}",
            file_path,
            suggestion="Check if the path is valid and you have write permissions"
        )
    except Exception as e:
        raise FileOperationError(
            f"Unexpected error writing file",
            file_path,
            details={"error_type": type(e).__name__, "error": str(e)}
        )


def ensure_directory(directory: str) -> Path:
    """Ensure directory exists, create if it doesn't"""
    if not directory or not directory.strip():
        raise ValidationError("Directory path cannot be empty", field="directory")
    
    path = Path(directory)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError as e:
        raise CustomPermissionError(directory, suggestion="Check permissions to create directory")
    except OSError as e:
        raise FileOperationError(
            f"Failed to create directory: {e}",
            directory,
            suggestion="Check if the path is valid"
        )
    except Exception as e:
        raise FileOperationError(
            f"Unexpected error creating directory",
            directory,
            details={"error_type": type(e).__name__, "error": str(e)}
        )
