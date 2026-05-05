"""Validation utilities for common checks."""

from typing import Optional


def is_empty_string(value: Optional[str]) -> bool:
    """Check if a string is empty or contains only whitespace.
    
    Args:
        value: String to check, or None
        
    Returns:
        True if the string is None, empty, or contains only whitespace
        
    Examples:
        >>> is_empty_string(None)
        True
        >>> is_empty_string("")
        True
        >>> is_empty_string("   ")
        True
        >>> is_empty_string("hello")
        False
    """
    return not value or not value.strip()


def validate_non_empty_string(value: Optional[str], field_name: str = "value") -> str:
    """Validate that a string is not empty.
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated string
        
    Raises:
        ValueError: If the string is empty or None
        
    Examples:
        >>> validate_non_empty_string("hello", "name")
        'hello'
        >>> validate_non_empty_string("", "name")
        ValueError: name cannot be empty
    """
    if is_empty_string(value):
        raise ValueError(f"{field_name} cannot be empty")
    return value
