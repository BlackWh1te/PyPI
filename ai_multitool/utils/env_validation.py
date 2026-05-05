"""Environment variable validation utilities."""

import os
from typing import Optional
from ai_multitool.core.exceptions import ValidationError


def get_env_var(
    var_name: str,
    default: Optional[str] = None,
    required: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> str:
    """Get and validate an environment variable.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if not set
        required: Whether the variable is required
        min_length: Minimum length validation
        max_length: Maximum length validation
        
    Returns:
        The validated environment variable value
        
    Raises:
        ValidationError: If validation fails
    """
    value = os.getenv(var_name, default)
    
    if required and (value is None or not value.strip()):
        raise ValidationError(
            f"Required environment variable '{var_name}' is not set",
            field=var_name
        )
    
    if value is None:
        if default is not None:
            return default
        raise ValidationError(
            f"Environment variable '{var_name}' is not set and no default provided",
            field=var_name
        )
    
    value = value.strip()
    
    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at least {min_length} characters",
            field=var_name
        )
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at most {max_length} characters",
            field=var_name
        )
    
    return value


def get_env_int(
    var_name: str,
    default: Optional[int] = None,
    required: bool = False,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> int:
    """Get and validate an integer environment variable.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if not set
        required: Whether the variable is required
        min_value: Minimum value validation
        max_value: Maximum value validation
        
    Returns:
        The validated integer value
        
    Raises:
        ValidationError: If validation fails
    """
    value_str = os.getenv(var_name)
    
    if required and value_str is None:
        raise ValidationError(
            f"Required environment variable '{var_name}' is not set",
            field=var_name
        )
    
    if value_str is None:
        if default is not None:
            return default
        raise ValidationError(
            f"Environment variable '{var_name}' is not set and no default provided",
            field=var_name
        )
    
    try:
        value = int(value_str)
    except ValueError:
        raise ValidationError(
            f"Environment variable '{var_name}' must be an integer",
            field=var_name
        )
    
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at least {min_value}",
            field=var_name
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at most {max_value}",
            field=var_name
        )
    
    return value


def get_env_float(
    var_name: str,
    default: Optional[float] = None,
    required: bool = False,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> float:
    """Get and validate a float environment variable.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if not set
        required: Whether the variable is required
        min_value: Minimum value validation
        max_value: Maximum value validation
        
    Returns:
        The validated float value
        
    Raises:
        ValidationError: If validation fails
    """
    value_str = os.getenv(var_name)
    
    if required and value_str is None:
        raise ValidationError(
            f"Required environment variable '{var_name}' is not set",
            field=var_name
        )
    
    if value_str is None:
        if default is not None:
            return default
        raise ValidationError(
            f"Environment variable '{var_name}' is not set and no default provided",
            field=var_name
        )
    
    try:
        value = float(value_str)
    except ValueError:
        raise ValidationError(
            f"Environment variable '{var_name}' must be a number",
            field=var_name
        )
    
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at least {min_value}",
            field=var_name
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"Environment variable '{var_name}' must be at most {max_value}",
            field=var_name
        )
    
    return value
