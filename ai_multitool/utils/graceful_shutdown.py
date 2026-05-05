"""Graceful shutdown handlers for ai-multitool."""

import signal
import sys
import time
import asyncio
from typing import Callable, Optional, List
from ai_multitool.utils.logging_config import get_logger

logger = get_logger(__name__)


class GracefulShutdown:
    """Graceful shutdown manager."""
    
    def __init__(self):
        """Initialize the graceful shutdown manager."""
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Handle SIGTERM (termination signal)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
        
        self.is_shutting_down = True
        
        # Run all shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {e}")
        
        # Exit gracefully
        sys.exit(0)
    
    def register_handler(self, handler: Callable) -> None:
        """Register a shutdown handler.
        
        Args:
            handler: Function to call on shutdown
        """
        self.shutdown_handlers.append(handler)
        logger.info(f"Registered shutdown handler: {handler.__name__}")
    
    def register_async_handler(self, handler: Callable) -> None:
        """Register an async shutdown handler.
        
        Args:
            handler: Async function to call on shutdown
        """
        async def async_wrapper():
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Error in async shutdown handler: {e}")
        
        # Store the wrapper
        self.shutdown_handlers.append(lambda: asyncio.run(async_wrapper()))
        logger.info(f"Registered async shutdown handler: {handler.__name__}")
    
    async def shutdown_async(self) -> None:
        """Trigger async shutdown.
        
        This is useful for async contexts where you want to
        trigger shutdown programmatically.
        """
        logger.info("Initiating graceful shutdown...")
        self.is_shutting_down = True
        
        # Run all shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {e}")


# Global shutdown manager instance
_shutdown_manager: Optional[GracefulShutdown] = None


def get_shutdown_manager() -> GracefulShutdown:
    """Get the global shutdown manager instance.
    
    Returns:
        GracefulShutdown instance
    """
    global _shutdown_manager
    if _shutdown_manager is None:
        _shutdown_manager = GracefulShutdown()
    return _shutdown_manager


def register_shutdown_handler(handler: Callable) -> None:
    """Register a shutdown handler with the global manager.
    
    Args:
        handler: Function to call on shutdown
    """
    manager = get_shutdown_manager()
    manager.register_handler(handler)


def on_shutdown(handler: Callable) -> Callable:
    """Decorator to register a function as a shutdown handler.
    
    Args:
        handler: Function to register
        
    Returns:
        The original function (unchanged)
    
    Example:
        @on_shutdown
        def cleanup():
            print("Cleaning up...")
    """
    register_shutdown_handler(handler)
    return handler


if __name__ == "__main__":
    # Example usage
    def cleanup_resources():
        print("Cleaning up resources...")
        # Your cleanup logic here
    
    def save_state():
        print("Saving state...")
        # Your state saving logic here
    
    manager = get_shutdown_manager()
    manager.register_handler(cleanup_resources)
    manager.register_handler(save_state)
    
    print("Graceful shutdown manager running. Press Ctrl+C to test.")
    
    # Simulate long-running process
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Signal handler will handle this
        pass
