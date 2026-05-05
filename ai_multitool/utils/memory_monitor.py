"""Memory monitoring and management utilities."""

import gc
import logging
from typing import Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - memory monitoring will be limited")


class MemoryMonitor:
    """Monitor and manage memory usage during operations."""
    
    def __init__(
        self,
        warning_threshold: float = 0.8,  # 80% memory usage
        critical_threshold: float = 0.9,  # 90% memory usage
        enable_gc: bool = True
    ):
        """Initialize memory monitor.
        
        Args:
            warning_threshold: Memory usage percentage to trigger warnings (0-1)
            critical_threshold: Memory usage percentage to trigger critical alerts (0-1)
            enable_gc: Whether to run garbage collection on high memory
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.enable_gc = enable_gc
        self.initial_memory = self.get_memory_info()
    
    def get_memory_info(self) -> dict:
        """Get current memory usage information.
        
        Returns:
            Dictionary with memory statistics
        """
        if not PSUTIL_AVAILABLE:
            return {"available": False}
        
        try:
            mem = psutil.virtual_memory()
            return {
                "available": True,
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent,
                "free": mem.free
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {"available": False, "error": str(e)}
    
    def check_memory(self) -> tuple[bool, str]:
        """Check if memory usage is within acceptable limits.
        
        Returns:
            Tuple of (is_ok, status_message)
        """
        if not PSUTIL_AVAILABLE:
            return True, "Memory monitoring not available"
        
        mem_info = self.get_memory_info()
        if not mem_info.get("available"):
            return True, "Memory info unavailable"
        
        percent = mem_info["percent"]
        
        if percent >= self.critical_threshold * 100:
            if self.enable_gc:
                gc.collect()
                # Recheck after GC
                mem_info = self.get_memory_info()
                percent = mem_info.get("percent", percent)
            
            if percent >= self.critical_threshold * 100:
                return False, f"CRITICAL: Memory usage at {percent:.1f}%"
            else:
                return True, f"Memory usage high ({percent:.1f}%), garbage collection helped"
        
        if percent >= self.warning_threshold * 100:
            return True, f"WARNING: Memory usage at {percent:.1f}%"
        
        return True, f"Memory usage OK ({percent:.1f}%)"
    
    def get_memory_delta(self) -> dict:
        """Get memory usage delta since initialization.
        
        Returns:
            Dictionary with memory change statistics
        """
        current = self.get_memory_info()
        if not current.get("available") or not self.initial_memory.get("available"):
            return {"available": False}
        
        return {
            "available": True,
            "used_delta": current["used"] - self.initial_memory["used"],
            "percent_delta": current["percent"] - self.initial_memory["percent"]
        }


def with_memory_monitor(
    warning_threshold: float = 0.8,
    critical_threshold: float = 0.9,
    enable_gc: bool = True
):
    """Decorator to monitor memory usage during function execution.
    
    Args:
        warning_threshold: Memory usage percentage to trigger warnings (0-1)
        critical_threshold: Memory usage percentage to trigger critical alerts (0-1)
        enable_gc: Whether to run garbage collection on high memory
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = MemoryMonitor(warning_threshold, critical_threshold, enable_gc)
            logger.info(f"Starting {func.__name__} - Initial memory: {monitor.get_memory_info()}")
            
            try:
                result = func(*args, **kwargs)
                
                # Check memory after execution
                is_ok, status = monitor.check_memory()
                delta = monitor.get_memory_delta()
                
                logger.info(f"Completed {func.__name__} - Memory status: {status}")
                if delta.get("available"):
                    logger.info(f"Memory delta: +{delta['used_delta']/1024/1024:.1f}MB, {delta['percent_delta']:+.1f}%")
                
                if not is_ok:
                    logger.error(f"Memory critical after {func.__name__}: {status}")
                
                return result
                
            except MemoryError as e:
                logger.critical(f"MemoryError in {func.__name__}: {e}")
                monitor.check_memory()  # Log current state
                raise
        
        return wrapper
    return decorator


def force_cleanup():
    """Force garbage collection and memory cleanup."""
    logger.info("Forcing garbage collection...")
    collected = gc.collect()
    logger.info(f"Garbage collection collected {collected} objects")
    
    if PSUTIL_AVAILABLE:
        mem_info = MemoryMonitor().get_memory_info()
        logger.info(f"Memory after cleanup: {mem_info}")


def get_safe_max_files_based_on_memory() -> int:
    """Calculate safe maximum files based on available memory.
    
    Returns:
        Safe maximum number of files to process
    """
    if not PSUTIL_AVAILABLE:
        return 100  # Conservative default
    
    try:
        mem = psutil.virtual_memory()
        available_mb = mem.available / 1024 / 1024
        
        # Assume average file size of 1MB for safety
        # Use 50% of available memory
        safe_files = int((available_mb * 0.5) / 1.0)
        
        # Cap at reasonable limits
        return max(10, min(safe_files, 1000))
    except Exception as e:
        logger.error(f"Failed to calculate safe max files: {e}")
        return 100
